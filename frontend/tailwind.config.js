/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                background: "#0B0C10",
                surface: "#1F2833",
                primary: "#66FCF1",
                secondary: "#45A29E",
                text: "#C5C6C7",
                accent: "#00E0FF", // Neon highlights
                card: "rgba(31, 40, 51, 0.7)",
            },
            fontFamily: {
                outfit: ['Outfit', 'sans-serif'],
                inter: ['Inter', 'sans-serif'],
            },
            backgroundImage: {
                'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
                'glass': 'linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0))',
            },
            boxShadow: {
                'neon': '0 0 15px rgba(102, 252, 241, 0.3)',
            }
        },
    },
    plugins: [],
}
