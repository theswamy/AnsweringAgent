import SwiftUI

@main
struct AnsweringAgentApp: App {
    @StateObject private var api = APIClient()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(api)
        }
    }
}

/// Shows onboarding until the server URL + API key are set, then the main tabs.
struct RootView: View {
    @EnvironmentObject var api: APIClient

    var body: some View {
        if api.isConfigured {
            MainTabView()
        } else {
            OnboardingView()
        }
    }
}

struct MainTabView: View {
    var body: some View {
        TabView {
            CallListView()
                .tabItem { Label("Calls", systemImage: "phone.bubble") }
            SettingsView()
                .tabItem { Label("Agent", systemImage: "person.wave.2") }
        }
    }
}
