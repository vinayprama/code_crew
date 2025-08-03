const API_BASE_URL = "http://localhost:8000";  // Change to your actual backend URL

// Helper function to make requests
async function apiRequest(endpoint, method = "GET", data = null, token = null) {
  const headers = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const options = {
    method,
    headers,
  };
  if (data) {
    options.body = JSON.stringify(data);
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
  const responseData = await response.json();

  if (!response.ok) {
    throw new Error(responseData.detail || "API request failed");
  }

  return responseData;
}

// ========== Chat ==========

// Send user message to chatbot
async function sendChatMessage(message, token) {
  return await apiRequest("/chat", "POST", { message }, token);
}

// Get previous chats
async function getChatHistory(token) {
  return await apiRequest("/chat/history", "GET", null, token);
}

    window.tailwind = window.tailwind || {};
    window.tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            primary: '#6366f1',
            secondary: '#f43f5e',
          },
          backgroundImage: {
            'animated': 'linear-gradient(-45deg, #e0eafc, #cfdef3, #e0eafc)',
          },
          animation: {
            gradient: 'gradientBG 10s ease infinite',
          },
          keyframes: {
            gradientBG: {
              '0%, 100%': { backgroundPosition: '0% 50%' },
              '50%': { backgroundPosition: '100% 50%' },
            },
          },
        }
      }
    };

    // the mainjs


    // Global variable for current project
    let currentProjectName = '';
    // Initialize Supabase client
    const supabaseUrl = 'https://dycssfukjwusfhrxwpgj.supabase.co';
    const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR5Y3NzZnVrand1c2Zocnh3cGdqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMwMTU0MTQsImV4cCI6MjA2ODU5MTQxNH0.WFIobEHLY9HyAuC8qWLtYoMPlOtpP6tdKEyjbvKVRzg';
    const supabaseClient = supabase.createClient(supabaseUrl, supabaseKey);
    // Load username
    async function loadUsername() {
      try {
        const { data: sessionData, error: sessionError } = await supabaseClient.auth.getSession();
        if (sessionError || !sessionData.session) {
          console.warn('No active session:', sessionError);
          document.getElementById('usernameDisplay').textContent = "Guest";
          return;
        }
        const userEmail = sessionData.session.user.email;
        const { data, error } = await supabaseClient
          .from('auth_users')
          .select('name')
          .eq('email', userEmail)
          .single();
        if (error) {
          console.error("Error fetching name from auth_users:", error);
          document.getElementById('usernameDisplay').textContent = "User";
        } else {
          document.getElementById('usernameDisplay').textContent = data.name;
        }
      } catch (err) {
        console.error("Error loading username:", err);
        document.getElementById('usernameDisplay').textContent = "User";
      }
    }
    // dark / light Theme toggle
    if (localStorage.getItem('theme') === 'dark') {
      document.documentElement.classList.add('dark');
      document.getElementById('iconDark')?.classList.add('hidden');
      document.getElementById('iconLight')?.classList.remove('hidden');
    }
    function toggleTheme() {
      const html = document.documentElement;
      const isDark = html.classList.toggle('dark');
      document.getElementById('iconDark')?.classList.toggle('hidden', isDark);
      document.getElementById('iconLight')?.classList.toggle('hidden', !isDark);
      localStorage.setItem('theme', isDark ? 'dark' : 'light');
    }
    // Sidebar toggle
    function toggleSidebar() {
      document.querySelector('aside')?.classList.toggle('hidden');
    }
    // Show section
    function showSection(sectionId) {
      console.log("Switching to section:", sectionId); // Debug
      document.getElementById('search').classList.add('hidden');
      document.getElementById('chat').classList.add('hidden');
      document.getElementById(sectionId).classList.remove('hidden');
    }
    document.getElementById('projectForm')?.addEventListener('submit', async e => {
  e.preventDefault();
  const projectName = document.getElementById('projectName').value.trim();
  if (!projectName) {
    alert("Please enter a project name.");
    return;
  }

  try {
    const checkRes = await fetch(`http://localhost:8001/upload/check_project/${projectName}`);
    const checkData = await checkRes.json();
    if (!checkData.exists) {
      alert("❌ Project not found in S3.");
      return;
    }

    currentProjectName = projectName;
    showSection('chat');

    // Optional: Preload context or ask first question here

  } catch (err) {
    console.error("Error checking project:", err);
    alert("❌ Failed to verify project in S3.");
  }
});
    // Chat form submission the search and start button in the userdashboard 
    document.getElementById('chatForm')?.addEventListener('submit', async e => {
      e.preventDefault();
      const msg = document.getElementById('userInput')?.value.trim();
      console.log("User Input:", msg, "Project Name:", currentProjectName); // Debug
      if (!msg || !currentProjectName) {
        alert("Please enter a message and ensure a project is selected.");
        return;
      }
      const chatWindow = document.getElementById('chatWindow');
      // User message display
      const userDiv = document.createElement('div');
      userDiv.textContent = msg;
      userDiv.className = 'text-right mb-2 text-gray-900 dark:text-white';
      chatWindow.appendChild(userDiv);
      // Loading shimmer
      const skeleton = document.createElement('div');
      skeleton.className = 'h-4 w-3/4 mb-2 rounded bg-gray-300 dark:bg-gray-700 animate-pulse shimmer';
      chatWindow.appendChild(skeleton);
      chatWindow.scrollTop = chatWindow.scrollHeight;
      document.getElementById('userInput').value = '';
      document.getElementById('userInput').focus();
      try {
        const res = await fetch("http://localhost:8001/chat/stream", {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_name: currentProjectName, query: msg })
        });
        if (!res.ok || !res.body) {
          const errorText = await res.text();
          throw new Error(errorText || 'Failed to get response from server');
        }
        const reader = res.body.getReader();
        const decoder = new TextDecoder("utf-8");
        chatWindow.removeChild(skeleton);
        const botDiv = document.createElement('div');
        botDiv.className = 'text-left mb-2 text-gray-700 dark:text-gray-300';
        chatWindow.appendChild(botDiv);
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          botDiv.textContent += decoder.decode(value);
          chatWindow.scrollTop = chatWindow.scrollHeight;
        }
      } catch (err) {
        console.error("Chat error:", err);
        chatWindow.removeChild(skeleton);
        const errDiv = document.createElement('div');
        errDiv.textContent = '⚠️ Error: ' + err.message;
        errDiv.className = 'text-left mb-2 text-red-500';
        chatWindow.appendChild(errDiv);
      }
    });
    // Drag & drop file upload in user dashboard 
    const dropArea = document.getElementById('drop-area');
    dropArea?.addEventListener('dragover', e => {
      e.preventDefault();
      dropArea.classList.add('highlight');
    });
    dropArea?.addEventListener('dragleave', () => {
      dropArea.classList.remove('highlight');
    });
    dropArea?.addEventListener('drop', async e => {
      e.preventDefault();
      dropArea.classList.remove('highlight');
      const file = e.dataTransfer.files[0];
      if (file) await uploadFile(file);
    });
    async function uploadFile(file) {
      if (!file.name.endsWith('.docx')) {
        alert("Only .docx files are supported.");
        return;
      }
      const projectName = prompt("Enter project name:");
      if (!projectName) {
        alert("Project name is required.");
        return;
      }
      try {
        const checkRes = await fetch(`http://localhost:8001/upload/check_project/${projectName}`);
        const checkData = await checkRes.json();
        if (checkData.exists) {
          const proceed = confirm(`Project "${projectName}" already exists. Upload to this project?`);
          if (!proceed) return;
        }
        const formData = new FormData();
        formData.append("file", file);
        formData.append("project_name", projectName);
        formData.append("user_id", "vinayprama07_gmail.com");
        const res = await fetch("http://localhost:8001/upload_doc", {
          method: "POST",
          body: formData
        });
        const result = await res.json();
        if (res.ok) {
          alert("✅ File uploaded successfully: " + result.message);
        } else {
          alert("❌ Upload failed: " + result.detail || "Unknown error");
        }
      } catch (err) {
        console.error("Upload error:", err);
        alert("❌ Upload failed.");
      }
    }
    // Voice mode for the user 
    const startBtn = document.getElementById('start-voice');
    const stopBtn = document.getElementById('stop-voice');
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.continuous = true;
    startBtn.onclick = () => {
      recognition.start();
      startBtn.classList.add('hidden');
      stopBtn.classList.remove('hidden');
      console.log("🎤 Voice mode activated");
    };
    stopBtn.onclick = () => {
      recognition.stop();
      startBtn.classList.remove('hidden');
      stopBtn.classList.add('hidden');
      console.log("🛑 Voice mode stopped");
    };
    recognition.onend = () => {
      if (!stopBtn.classList.contains('hidden')) {
        console.log("🔄 Auto-restarting voice recognition");
        recognition.start();
      }
    };
    recognition.onerror = (event) => {
      console.error("Speech recognition error:", event.error);
    };
    recognition.onresult = async (event) => {
      const transcript = event.results[event.results.length - 1][0].transcript.trim();
      console.log("🗣️ You said:", transcript);
      try {
        const res = await fetch("http://localhost:8001/chat/voice", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            query: transcript,
            project_name: currentProjectName || "Smart Traffic AI",
          })
        });
        const data = await res.json();
        console.log("🤖 Bot replies:", data.reply);
        const utterance = new SpeechSynthesisUtterance(data.reply);
        utterance.lang = 'en-US';
        speechSynthesis.speak(utterance);
      } catch (err) {
        console.error("Fetch or TTS error:", err);
      }
    };
    // Onboarding tour
    const tourSteps = [
      { title: "👋 Welcome to Prama AI", text: "Welcome to Prama AI — your intelligent project assistant!" },
      { title: "🔍 Project Search Box", text: "Start by entering your project name here. We'll fetch the related documents from SharePoint securely.", highlight: "#projectName" },
      { title: "🤖 Smart Chatbot", text: "Ask anything related to your project! Our AI bot will read your SharePoint documents and give accurate answers.", highlight: "#chatWindow" },
      { title: "😕 Didn't get it?", text: "If you're ever confused or don’t understand the bot’s reply, just say so — we’ll schedule a live meeting with a team member." },
      { title: "👥 Team Collaboration", text: "You're not alone — your team members are connected to the same project. We’ll notify the right person when needed." },
      { title: "🛡️ Safe & Secure", text: "All your data is stored safely with Supabase and document access is encrypted and controlled per project." },
      { title: "🎉 You're Ready!", text: "That’s it! You’re ready to explore Prama AI. Let’s make project management smarter.", final: true }
    ];
    let currentStep = 0;
    const onboardingEl = document.getElementById('onboarding');
    const stepTitle = document.getElementById('stepTitle');
    const stepText = document.getElementById('stepText');
    const nextBtn = document.getElementById('nextBtn');
    const prevBtn = document.getElementById('prevBtn');
    function showTour() {
      onboardingEl?.classList.remove('hidden');
      loadStep(0);
    }
    function loadStep(i) {
      const step = tourSteps[i];
      stepTitle.textContent = step.title;
      stepText.textContent = step.text;
      prevBtn.disabled = i === 0;
      nextBtn.textContent = step.final ? 'Start Using Now' : 'Next';
      document.querySelectorAll('.ring-yellow-400').forEach(el =>
        el.classList.remove('ring', 'ring-yellow-400', 'ring-offset-2')
      );
      if (step.highlight) {
        document.querySelector(step.highlight)?.classList.add('ring', 'ring-yellow-400', 'ring-offset-2');
      }
    }
    nextBtn?.addEventListener('click', () => {
      if (currentStep < tourSteps.length - 1) {
        currentStep++;
        loadStep(currentStep);
      } else {
        closeTour();
      }
    });
    prevBtn?.addEventListener('click', () => {
      if (currentStep > 0) {
        currentStep--;
        loadStep(currentStep);
      }
    });
    function closeTour() {
      onboardingEl?.classList.add('hidden');
      document.querySelectorAll('.ring-yellow-400').forEach(el =>
        el.classList.remove('ring', 'ring-yellow-400', 'ring-offset-2')
      );
    }
    // Initialize on load
    window.addEventListener('load', () => {
      loadUsername();
      if (!localStorage.getItem('tourDone')) {
        showTour();
        localStorage.setItem('tourDone', true);
      }
    });
  