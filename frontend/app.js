const menuItems = [
    {
        title: 'ECE 20001',
        items: ['Course Info', 'Syllabus', 'Homework Help', 'Code Debug'],
        bgImage: 'https://cdn-icons-png.flaticon.com/512/3176/3176298.png' // Circuit icon
    },
    {
        title: 'ECE 20002',
        items: ['Course Info', 'Syllabus', 'Homework Help', 'Code Debug'],
        bgImage: 'https://cdn-icons-png.flaticon.com/512/1055/1055683.png' // Wrench icon
    },
    {
        title: 'ECE 20875',
        items: ['Course Info', 'Syllabus', 'Homework Help', 'Code Debug'],
        bgImage: 'https://cdn-icons-png.flaticon.com/512/2888/2888407.png' // Computer icon
    }
];

const socialLinks = [
    {
        name: 'Purdue Website',
        url: 'https://www.purdue.edu',
        icon: 'https://cdn-icons-png.flaticon.com/512/8324/8324431.png' // University icon
    },
    {
        name: 'Engineering',
        url: 'https://engineering.purdue.edu',
        icon: 'https://cdn-icons-png.flaticon.com/512/3176/3176291.png' // Engineering icon
    },
    {
        name: 'LinkedIn',
        url: 'https://www.linkedin.com/school/purdue-university',
        icon: 'https://cdn-icons-png.flaticon.com/512/3536/3536505.png' // LinkedIn icon
    },
    {
        name: 'YouTube',
        url: 'https://www.youtube.com/user/PurdueUniversity',
        icon: 'https://cdn-icons-png.flaticon.com/512/3670/3670147.png' // YouTube icon
    }
];

function AuthModal({ isOpen, onClose, isSignUp, setIsSignUp }) {
    if (!isOpen) return null;
        
    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-secondary rounded-lg p-8 relative max-w-md w-full mx-4">
                {/* Close button */}
                <button 
                    onClick={onClose}
                    className="absolute top-4 right-4 text-gold hover:text-gold/80 transition-colors"
                >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>

                <h2 className="text-2xl font-bold text-gold mb-6 text-center">
                    {isSignUp ? 'Create Account' : 'Welcome Back'}
                </h2>



                
                <form
                    className="space-y-4"
                    onSubmit={(e) => {
                        e.preventDefault();

                        const formData = new FormData(e.target);
                        const email = formData.get("email");
                        const username = formData.get("username");
                        const password = formData.get("password");
                        const confirmPassword = formData.get("confirmPassword");

                        if (isSignUp) {
                        if (!email || !username || !password || !confirmPassword) {
                            alert("Please fill out all fields.");
                            return;
                        }
                        if (password !== confirmPassword) {
                            alert("Passwords do not match.");
                            return;
                        }

                        fetch("http://localhost:8888/api/register", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ user_id: username, email, password }),
                        })
                            .then((res) => res.json())
                            .then((data) => {
                            if (data.status === "Register Success.") {
                                alert("Account created! Please log in.");
                                setIsSignUp(false);
                            } else {
                                alert("Registration failed: " + data.status);
                            }
                            });
                        } else {
                        const loginUsername = formData.get("username");
                        const loginPassword = formData.get("password");

                        fetch("http://localhost:8888/api/login", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            credentials: "include",
                            body: JSON.stringify({ user_id: loginUsername, password: loginPassword }),
                        })
                            .then((res) => res.json())
                            .then((data) => {
                            if (data.status === "Login Success.") {
                                alert("Login successful!");
                                onClose();
                                login({ user_id: loginUsername }); // <--- This must be defined
                            } else {
                                alert("Login failed: " + data.status);
                            }
                            });
                        }
                    }}
                    >
                    {isSignUp && (
                        <div>
                        <label className="block text-gold mb-2">Email</label>
                        <input
                            name="email"
                            type="email"
                            className="w-full p-3 rounded-lg bg-primary border-2 border-gold/30 focus:border-gold focus:outline-none text-white"
                        />
                        </div>
                    )}

                    <div>
                        <label className="block text-gold mb-2">Username</label>
                        <input
                        name="username"
                        type="text"
                        className="w-full p-3 rounded-lg bg-primary border-2 border-gold/30 focus:border-gold focus:outline-none text-white"
                        />
                    </div>

                    <div>
                        <label className="block text-gold mb-2">Password</label>
                        <input
                        name="password"
                        type="password"
                        className="w-full p-3 rounded-lg bg-primary border-2 border-gold/30 focus:border-gold focus:outline-none text-white"
                        />
                    </div>

                    {isSignUp && (
                        <div>
                        <label className="block text-gold mb-2">Confirm Password</label>
                        <input
                            name="confirmPassword"
                            type="password"
                            className="w-full p-3 rounded-lg bg-primary border-2 border-gold/30 focus:border-gold focus:outline-none text-white"
                        />
                        </div>
                    )}

                    <button
                        type="submit"
                        className="w-full py-3 bg-gold text-black rounded-lg font-semibold hover:bg-gold/90 transition-colors"
                    >
                        {isSignUp ? "Sign Up" : "Log In"}
                    </button>
</form>


                <div className="mt-4 text-center">
                    {!isSignUp && (
                        <button className="text-gold/80 hover:text-gold text-sm">
                            Forgot Password?
                        </button>
                    )}
                    <div className="mt-2">
                        <button 
                            onClick={() => setIsSignUp(!isSignUp)}
                            className="text-gold hover:text-gold/80 text-sm"
                        >
                            {isSignUp ? 'Already have an account? Log in' : "Don't have an account? Sign up"}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

function App() {
    // Initialize theme from localStorage, default to true (dark mode) if not set
    const [isDarkMode, setIsDarkMode] = React.useState(() => {
        const savedTheme = localStorage.getItem('isDarkMode');
        return savedTheme !== null ? JSON.parse(savedTheme) : true;
    });
    const [isAuthOpen, setIsAuthOpen] = React.useState(false);
    const [isSignUp, setIsSignUp] = React.useState(false);

    // Update localStorage when theme changes
    React.useEffect(() => {
        localStorage.setItem('isDarkMode', JSON.stringify(isDarkMode));
        // Update body class for global theme
        document.body.classList.toggle('dark-mode', isDarkMode);
        document.body.classList.toggle('light-mode', !isDarkMode);
    }, [isDarkMode]);

    return (
        <div className={`min-h-screen ${isDarkMode ? 'bg-[#111111]' : 'bg-light-primary'} text-white flex flex-col`}>
            {/* Navigation Bar */}
            <nav className={`${isDarkMode ? 'bg-secondary' : 'bg-light-secondary'} border-b border-gold/30`}>
                <div className="container mx-auto px-4">
                    <div className="flex items-center justify-between h-14">
                        {/* Left side - Navigation */}
                        <div className="flex items-center">
                            <p className="text-gold/80 text-sm mr-8">
                                © 2025 Purdue University. All rights reserved.
                            </p>
                            <div className="h-8 w-px bg-gold/30 hidden md:block"></div>
                            <div className="flex items-center space-x-4 ml-8">
                                <a 
                                    href="https://www.purdue.edu" 
                                    target="_blank" 
                                    rel="noopener noreferrer"
                                    className="text-gold/80 hover:text-gold transition-colors"
                                >
                                    <img src="https://cdn-icons-png.flaticon.com/512/8324/8324431.png" alt="Purdue Website" className="w-6 h-6 opacity-80 hover:opacity-100 transition-opacity" />
                                </a>
                                <a 
                                    href="https://engineering.purdue.edu" 
                                    target="_blank" 
                                    rel="noopener noreferrer"
                                    className="text-gold/80 hover:text-gold transition-colors"
                                >
                                    <img src="https://cdn-icons-png.flaticon.com/512/3176/3176291.png" alt="Engineering" className="w-6 h-6 opacity-80 hover:opacity-100 transition-opacity" />
                                </a>
                                <a 
                                    href="https://www.linkedin.com/school/purdue-university" 
                                    target="_blank" 
                                    rel="noopener noreferrer"
                                    className="text-gold/80 hover:text-gold transition-colors"
                                >
                                    <img src="https://cdn-icons-png.flaticon.com/512/3536/3536505.png" alt="LinkedIn" className="w-6 h-6 opacity-80 hover:opacity-100 transition-opacity" />
                                </a>
                                <a 
                                    href="https://www.youtube.com/user/PurdueUniversity" 
                                    target="_blank" 
                                    rel="noopener noreferrer"
                                    className="text-gold/80 hover:text-gold transition-colors"
                                >
                                    <img src="https://cdn-icons-png.flaticon.com/512/3670/3670147.png" alt="YouTube" className="w-6 h-6 opacity-80 hover:opacity-100 transition-opacity" />
                                </a>
                            </div>
                        </div>

                        {/* Right side - Theme and Auth */}
                        <div className="flex items-center space-x-4">
                            {/* Theme Toggle */}
                            <button
                                onClick={() => setIsDarkMode(!isDarkMode)}
                                className="text-gold hover:text-gold/80 transition-colors p-2"
                            >
                                {isDarkMode ? (
                                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                                        <path d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" />
                                    </svg>
                                ) : (
                                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                                        <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
                                    </svg>
                                )}
                            </button>

                            {/* User Profile */}
                            <button
                                onClick={() => {
                                    setIsAuthOpen(true);
                                    setIsSignUp(false);
                                }}
                                className="text-gold hover:text-gold/80 transition-colors p-2"
                            >
                                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                </svg>
                            </button>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Main Content */}
            <main className="container mx-auto px-4 flex-grow">
                {/* Header with Pete */}
                <div className="text-center mt-16 mb-20">
                    <h1 className="text-6xl md:text-7xl font-bold text-gold mb-6 fancy-title fade-in-initial">
                        Hi, I'm Professor Pete!
                    </h1>
                    <h2 className="text-4xl md:text-5xl text-gold fancy-title fade-in-initial">
                        How Can I Help You?
                    </h2>
                    <div className="w-40 h-40 rounded-full border-4 border-gold overflow-hidden mx-auto mt-8 fade-in-initial">
                        <img 
                            src="img_9750.gif"
                            alt="Professor Pete Animation"
                            className="w-full h-full object-cover"
                        />
                    </div>
                </div>

                {/* Course Boxes */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-[90rem] mx-auto mb-16 fade-in-boxes">
                    {menuItems.map((menu, index) => (
                        <div
                            key={menu.title}
                            className="relative group cursor-pointer overflow-hidden"
                        >
                            <div className="aspect-[4/3] bg-secondary rounded-xl border-2 border-gold transition-all relative flex flex-col items-center justify-center p-4">
                                {/* Background Icon */}
                                <div className="absolute inset-0 flex items-center justify-center opacity-15">
                                    <img 
                                        src={menu.bgImage}
                                        alt="Background Icon"
                                        className="w-3/4 h-3/4 object-contain transition-transform duration-300 group-hover:scale-110"
                                    />
                                </div>
                                {/* Content */}
                                <div className="relative z-10 w-full h-full flex flex-col items-center justify-center transition-all duration-300 transform group-hover:-translate-y-4">
                                    <h3 className="text-5xl font-bold text-gold text-center mb-4 transition-all duration-300 group-hover:text-3xl group-hover:mb-8">
                                        {menu.title}
                                    </h3>
                                    <div className="grid grid-cols-2 gap-6 opacity-0 group-hover:opacity-100 transition-all duration-300 w-full px-4">
                                        {menu.items.map((item) => (
                                            <a
                                                key={item}
                                                href={`course-page.html?course=${menu.title}&section=${item}`}
                                                className="block text-center py-4 px-4 hover:text-accent bg-black bg-opacity-50 rounded-lg transition-colors border border-gold/30"
                                            >
                                                {item}
                                            </a>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </main>

            {/* Footer */}
            <footer className="bg-secondary py-4 border-t border-gold/30">
                <div className="container mx-auto px-4">
                    <div className="flex flex-col md:flex-row items-center justify-between">
                        <p className="text-gold/80 text-sm mb-4 md:mb-0">
                            © 2025 Purdue University. All rights reserved.
                        </p>
                        <div className="flex items-center space-x-6">
                            {socialLinks.map((link) => (
                                <a
                                    key={link.name}
                                    href={link.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-gold/80 hover:text-gold transition-colors"
                                    title={link.name}
                                >
                                    <img 
                                        src={link.icon} 
                                        alt={link.name}
                                        className="w-6 h-6 opacity-80 hover:opacity-100 transition-opacity"
                                    />
                                </a>
                            ))}
                        </div>
                    </div>
                </div>
            </footer>

            {/* Auth Modal */}
            <AuthModal 
                isOpen={isAuthOpen}
                onClose={() => setIsAuthOpen(false)}
                isSignUp={isSignUp}
                setIsSignUp={setIsSignUp}
            />
        </div>
    );
}

ReactDOM.render(<App />, document.getElementById('root')); 