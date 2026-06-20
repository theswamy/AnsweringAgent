import SwiftUI

/// One call: the agent's summary, callback details, and the full transcript as
/// a chat-style thread.
struct CallDetailView: View {
    @EnvironmentObject var api: APIClient
    let callSid: String

    @State private var call: CallLog?
    @State private var loading = true
    @State private var error: String?

    var body: some View {
        Group {
            if let call {
                content(call)
            } else if loading {
                ProgressView()
            } else {
                Text(error ?? "Couldn't load this call.").foregroundStyle(.secondary)
            }
        }
        .navigationTitle(call?.displayName ?? "Call")
        .navigationBarTitleDisplayMode(.inline)
        .task { await load() }
    }

    private func content(_ call: CallLog) -> some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                if let summary = call.summary, !summary.isEmpty {
                    Card(title: "Summary", systemImage: "text.quote") {
                        Text(summary)
                    }
                }

                if call.wantsCallback {
                    Card(title: "Callback requested", systemImage: "phone.arrow.up.right") {
                        if let n = call.callbackNumber, !n.isEmpty {
                            LabeledContent("Number", value: n)
                        }
                        if let t = call.callbackTime, !t.isEmpty {
                            LabeledContent("When", value: t)
                        }
                    }
                }

                Card(title: "Details", systemImage: "info.circle") {
                    if let from = call.fromNumber { LabeledContent("From", value: from) }
                    LabeledContent("When", value: RelativeTime.format(call.startedAt))
                    LabeledContent("Caller", value: call.automated ? "Automated / IVR" : "Person")
                }

                Text("Transcript").font(.headline).padding(.top, 4)
                ForEach(call.turns ?? []) { turn in
                    TranscriptBubble(turn: turn)
                }
            }
            .padding()
        }
    }

    private func load() async {
        loading = true
        defer { loading = false }
        do { call = try await api.getCall(callSid) }
        catch { error = (error as? LocalizedError)?.errorDescription ?? error.localizedDescription }
    }
}

private struct TranscriptBubble: View {
    let turn: Turn

    var body: some View {
        HStack {
            if turn.isAgent { Spacer(minLength: 40) }
            Text(turn.text)
                .padding(10)
                .background(turn.isAgent ? Color.blue.opacity(0.15) : Color.gray.opacity(0.15))
                .clipShape(RoundedRectangle(cornerRadius: 14))
            if !turn.isAgent { Spacer(minLength: 40) }
        }
    }
}

private struct Card<Content: View>: View {
    let title: String
    let systemImage: String
    @ViewBuilder var content: Content

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Label(title, systemImage: systemImage)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(.secondary)
            content
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color(.secondarySystemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 16))
    }
}
