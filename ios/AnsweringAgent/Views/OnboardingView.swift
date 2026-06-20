import SwiftUI

/// First-run setup: point the app at your deployed backend and enter the shared
/// API key. These are stored on-device via @AppStorage.
struct OnboardingView: View {
    @EnvironmentObject var api: APIClient
    @State private var url = ""
    @State private var key = ""
    @State private var testing = false
    @State private var error: String?

    var body: some View {
        NavigationStack {
            Form {
                Section {
                    Text("Connect to your answering-agent server. This is the backend you deployed that answers your forwarded calls.")
                        .font(.callout)
                        .foregroundStyle(.secondary)
                }
                Section("Server") {
                    TextField("https://your-server.example.com", text: $url)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                        .keyboardType(.URL)
                    SecureField("API key", text: $key)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                }
                if let error {
                    Section { Text(error).foregroundStyle(.red) }
                }
                Section {
                    Button {
                        Task { await connect() }
                    } label: {
                        if testing { ProgressView() } else { Text("Connect") }
                    }
                    .disabled(url.isEmpty || key.isEmpty || testing)
                }
            }
            .navigationTitle("Set up agent")
        }
    }

    private func connect() async {
        testing = true
        error = nil
        // Stash the values so the client uses them, then verify with a real call.
        api.serverURL = url.trimmingCharacters(in: .whitespaces)
        api.apiKey = key.trimmingCharacters(in: .whitespaces)
        do {
            _ = try await api.fetchSettings()
            // Success: isConfigured becomes true and RootView swaps to the tabs.
        } catch {
            self.error = (error as? LocalizedError)?.errorDescription ?? error.localizedDescription
            api.serverURL = ""
            api.apiKey = ""
        }
        testing = false
    }
}
