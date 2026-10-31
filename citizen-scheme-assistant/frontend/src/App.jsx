import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { LanguageProvider } from './i18n/LanguageContext';
import { Navbar } from './components/common/Navbar';
import { Footer } from './components/common/Footer';
import { HomePage } from './pages/HomePage';
import { SchemesPage } from './pages/SchemesPage';
import { ScreeningPage } from './pages/ScreeningPage';
import { ResultsPage } from './pages/ResultsPage';
import { SchemeDetailsPage } from './pages/SchemeDetailsPage';
import { VoiceDiagnosticPage } from './pages/VoiceDiagnosticPage';
import { NotFoundPage } from './pages/NotFoundPage';
import { LoginPage } from './pages/LoginPage';
import { SignupPage } from './pages/SignupPage';
import { ProfilePage } from './pages/ProfilePage';
import { AuthProvider } from './auth/AuthContext';
import { ProtectedRoute } from './auth/ProtectedRoute';
import { ProfileDetailsPage } from './profile/ProfileDetailsPage';
import { FloatingChatbot } from './components/chatbot/FloatingChatbot';

export const App = () => {
  return (
    <LanguageProvider>
      <AuthProvider>
        <Router>
          <div className="min-h-screen flex flex-col selection:bg-orange-200 selection:text-orange-950">
            <Navbar />
            <main className="flex-1 flex flex-col">
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/schemes" element={<SchemesPage />} />
                <Route path="/schemes/:code" element={<SchemeDetailsPage />} />
                <Route path="/screening" element={<ScreeningPage />} />
                <Route path="/results" element={<ResultsPage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/signup" element={<SignupPage />} />
                <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
                <Route path="/profile/details" element={<ProtectedRoute><ProfileDetailsPage /></ProtectedRoute>} />
                <Route path="/voice-diagnostic" element={<VoiceDiagnosticPage />} />
                <Route path="*" element={<NotFoundPage />} />
              </Routes>
            </main>
            <Footer />

            {/* YojanaMitra Floating AI Assistant Chatbot */}
            <FloatingChatbot />
          </div>
        </Router>
      </AuthProvider>
    </LanguageProvider>
  );
};

export default App;
