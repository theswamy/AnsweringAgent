import SwiftUI

/// Configure how the agent behaves: your name (used in the greeting), where to
/// text transcripts, and the default instructions for automated callers / IVRs.
struct SettingsView: View {
    @EnvironmentObject var api: APIClient

    @State private var settings: AgentSettings?
    @State private var userName = ""
    @State private var userPhone = ""
    @State private var agentDefaults = ""
    @State private var smsEnabled = true

    @State private var loading = true
    @State private var saving = false
    @State private var status: String?

    var body: some View {
        NavigationStack {
            Form {
                if loading {
                    ProgressView()
                } else {
                    Section("Your details") {
                        TextField("Your name", text: $userName)
                        Text("Greeting: “Hi - this is \(userName.isEmpty ? "…" : userName)'s agent, \(userName.isEmpty ? "…" : userName) isn't available. Who is speaking?”")
                            .font(.caption).foregroundStyle(.secondary)
                    }
                    Section("Transcript delivery") {
                        Toggle("Text me each transcript", isOn: $smsEnabled)
                        TextField("Your phone (+1…)", text: $userPhone)
                            .keyboardType(.phonePad)
                            .disabled(!smsEnabled)
                    }
                    Section("Defaults for automated callers / IVRs") {
                        TextEditor(text: $agentDefaults)
                            .frame(minHeight: 120)
                        Text("Used when the caller is a robocall, phone menu, or another AI agent.")
                            .font(.caption).foregroundStyle(.secondary)
                    }
                    if let status {
                        Section { Text(status).foregroundStyle(.secondary) }
                    }
                    Section {
                        Button {
                            Task { await save() }
                        } label: {
                            if saving { ProgressView() } else { Text("Save") }
                        }
                        .disabled(saving)
                        Button("Disconnect server", role: .destructive) {
                            api.serverURL = ""
                            api.apiKey = ""
                        }
                    }
                }
            }
            .navigationTitle("Agent")
            .task { await load() }
        }
    }

    private func load() async {
        loading = true
        defer { loading = false }
        do {
            let s = try await api.fetchSettings()
            settings = s
            userName = s.userName
            userPhone = s.userPhone
            agentDefaults = s.agentDefaults
            smsEnabled = s.smsEnabled
        } catch {
            status = (error as? LocalizedError)?.errorDescription ?? error.localizedDescription
        }
    }

    private func save() async {
        saving = true
        defer { saving = false }
        let update = SettingsUpdate(
            userName: userName,
            userPhone: userPhone,
            agentDefaults: agentDefaults,
            sendTranscriptSms: smsEnabled
        )
        do {
            settings = try await api.updateSettings(update)
            status = "Saved."
        } catch {
            status = (error as? LocalizedError)?.errorDescription ?? error.localizedDescription
        }
    }
}
