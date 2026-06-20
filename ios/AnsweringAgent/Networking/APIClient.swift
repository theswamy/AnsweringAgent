import Foundation
import SwiftUI

/// Talks to the answering-agent backend. The server URL and API key are stored
/// on-device (set during onboarding) and sent on every request.
@MainActor
final class APIClient: ObservableObject {
    @AppStorage("serverURL") var serverURL: String = ""
    @AppStorage("apiKey") var apiKey: String = ""

    /// Onboarding is complete once we have somewhere to talk to and a key.
    var isConfigured: Bool {
        !serverURL.trimmingCharacters(in: .whitespaces).isEmpty
            && !apiKey.trimmingCharacters(in: .whitespaces).isEmpty
    }

    enum APIError: LocalizedError {
        case badURL, unauthorized, server(Int), decoding

        var errorDescription: String? {
            switch self {
            case .badURL: return "The server URL is not valid."
            case .unauthorized: return "API key was rejected by the server."
            case .server(let code): return "Server returned an error (\(code))."
            case .decoding: return "Couldn't read the server's response."
            }
        }
    }

    private func makeDecoder() -> JSONDecoder {
        let d = JSONDecoder()
        d.keyDecodingStrategy = .convertFromSnakeCase
        return d
    }

    private func request(_ path: String, method: String = "GET", body: Data? = nil) throws -> URLRequest {
        guard let url = URL(string: serverURL.trimmingCharacters(in: .whitespaces) + path) else {
            throw APIError.badURL
        }
        var req = URLRequest(url: url)
        req.httpMethod = method
        req.setValue(apiKey, forHTTPHeaderField: "X-API-Key")
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.httpBody = body
        return req
    }

    private func send<T: Decodable>(_ req: URLRequest, as type: T.Type) async throws -> T {
        let (data, response) = try await URLSession.shared.data(for: req)
        guard let http = response as? HTTPURLResponse else { throw APIError.server(-1) }
        if http.statusCode == 401 { throw APIError.unauthorized }
        guard (200..<300).contains(http.statusCode) else { throw APIError.server(http.statusCode) }
        do {
            return try makeDecoder().decode(T.self, from: data)
        } catch {
            throw APIError.decoding
        }
    }

    // MARK: - Endpoints

    func fetchSettings() async throws -> AgentSettings {
        try await send(request("/api/settings"), as: AgentSettings.self)
    }

    func updateSettings(_ update: SettingsUpdate) async throws -> AgentSettings {
        let encoder = JSONEncoder()
        encoder.keyEncodingStrategy = .convertToSnakeCase
        let body = try encoder.encode(update)
        return try await send(request("/api/settings", method: "PUT", body: body), as: AgentSettings.self)
    }

    func listCalls() async throws -> [CallLog] {
        try await send(request("/api/calls"), as: [CallLog].self)
    }

    func getCall(_ callSid: String) async throws -> CallLog {
        try await send(request("/api/calls/\(callSid)"), as: CallLog.self)
    }
}
