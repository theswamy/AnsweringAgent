import Foundation

/// A single call the agent handled. Mirrors the backend `calls` row.
struct CallLog: Codable, Identifiable, Hashable {
    var callSid: String
    var fromNumber: String?
    var toNumber: String?
    var startedAt: String
    var endedAt: String?
    var status: String
    var callerName: String?
    var intent: String?
    var callbackRequested: Int
    var callbackNumber: String?
    var callbackTime: String?
    var isAutomated: Int
    var summary: String?

    // Present only when fetching a single call.
    var turns: [Turn]?
    var transcript: String?

    var id: String { callSid }
    var wantsCallback: Bool { callbackRequested == 1 }
    var automated: Bool { isAutomated == 1 }
    var displayName: String { callerName ?? fromNumber ?? "Unknown caller" }
}

/// One line of the conversation. `role` is "agent" or "caller".
struct Turn: Codable, Identifiable, Hashable {
    var role: String
    var text: String
    var createdAt: String

    var id: String { createdAt + role + text }
    var isAgent: Bool { role == "agent" }
}

/// The user-editable behaviour of the agent. Mirrors the backend `settings` row.
struct AgentSettings: Codable, Hashable {
    var userName: String
    var userPhone: String
    var agentDefaults: String
    var sendTranscriptSms: Int

    var smsEnabled: Bool { sendTranscriptSms == 1 }
}

/// Body for PUT /api/settings.
struct SettingsUpdate: Codable {
    var userName: String?
    var userPhone: String?
    var agentDefaults: String?
    var sendTranscriptSms: Bool?
}
