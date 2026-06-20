import SwiftUI

/// The list of calls the agent has handled, newest first. Pull to refresh.
struct CallListView: View {
    @EnvironmentObject var api: APIClient
    @State private var calls: [CallLog] = []
    @State private var loading = false
    @State private var error: String?

    var body: some View {
        NavigationStack {
            Group {
                if calls.isEmpty && !loading {
                    ContentUnavailableView(
                        "No calls yet",
                        systemImage: "phone.down",
                        description: Text("When your agent answers a forwarded call, it shows up here with the full transcript.")
                    )
                } else {
                    List(calls) { call in
                        NavigationLink(value: call) {
                            CallRow(call: call)
                        }
                    }
                }
            }
            .navigationTitle("Calls")
            .navigationDestination(for: CallLog.self) { call in
                CallDetailView(callSid: call.callSid)
            }
            .toolbar {
                if loading { ProgressView() }
            }
            .refreshable { await load() }
            .task { await load() }
            .alert("Couldn't load calls", isPresented: .constant(error != nil)) {
                Button("OK") { error = nil }
            } message: { Text(error ?? "") }
        }
    }

    private func load() async {
        loading = true
        defer { loading = false }
        do { calls = try await api.listCalls() }
        catch { self.error = (error as? LocalizedError)?.errorDescription ?? error.localizedDescription }
    }
}

private struct CallRow: View {
    let call: CallLog

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text(call.displayName).font(.headline)
                if call.automated {
                    Image(systemName: "cpu").foregroundStyle(.secondary)
                }
                Spacer()
                if call.wantsCallback {
                    Image(systemName: "phone.arrow.up.right").foregroundStyle(.blue)
                }
            }
            if let intent = call.intent, !intent.isEmpty {
                Text(intent).font(.subheadline).foregroundStyle(.secondary).lineLimit(2)
            }
            Text(RelativeTime.format(call.startedAt))
                .font(.caption).foregroundStyle(.tertiary)
        }
        .padding(.vertical, 2)
    }
}

/// Formats an ISO-8601 timestamp as a friendly relative string.
enum RelativeTime {
    static func format(_ iso: String) -> String {
        let parser = ISO8601DateFormatter()
        parser.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        let date = parser.date(from: iso) ?? ISO8601DateFormatter().date(from: iso)
        guard let date else { return iso }
        let f = RelativeDateTimeFormatter()
        f.unitsStyle = .abbreviated
        return f.localizedString(for: date, relativeTo: Date())
    }
}
