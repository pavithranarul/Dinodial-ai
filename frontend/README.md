# Masala of India - Restaurant Landing Page

A beautiful, responsive restaurant landing page built with React.js and Vite, featuring a table booking system with backend API integration.

## Features

- **Modern UI Design** - Inspired by masalaofindia.com with warm, appetizing color scheme
- **Hero Section** - Full-screen hero with prominent "Book a Table" CTA button
- **About Section** - Restaurant information with features showcase
- **Menu Section** - Grid layout displaying signature dishes with prices
- **Contact Section** - Contact information and social media links
- **Booking Modal** - Interactive form for table reservations with:
  - **Auto-popup** - Automatically appears after 15 seconds OR when user scrolls
  - Name and phone number validation
  - UUID generation for each booking
  - API integration with dummy endpoint
  - Success/error feedback
  - Beautiful animations and transitions
  - Smart detection - only shows once per session

## Tech Stack

- **React 18.2** - Frontend framework
- **Vite 5.0** - Build tool and dev server
- **CSS3** - Styling with gradients, animations, and responsive design
- **Fetch API** - HTTP requests to backend
- **crypto.randomUUID()** - Native browser UUID generation

## Getting Started

### Prerequisites

- Node.js (version 14 or higher)
- npm or yarn package manager

### Installation

1. Clone or navigate to this directory:
   ```bash
   cd Dinodial-hackathon
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open your browser and visit:
   ```
   http://localhost:5173
   ```

### Build for Production

To create a production build:
```bash
npm run build
```

To preview the production build:
```bash
npm run preview
```

## Project Structure

```
Dinodial-hackathon/
├── src/
│   ├── components/
│   │   ├── Hero.jsx & Hero.css          # Hero section with CTA
│   │   ├── About.jsx & About.css        # About section
│   │   ├── Menu.jsx & Menu.css          # Menu showcase
│   │   ├── Contact.jsx & Contact.css    # Contact info
│   │   └── BookingModal.jsx & .css      # Booking form modal
│   ├── App.jsx                          # Main app component
│   ├── App.css                          # Global styles
│   └── main.jsx                         # React entry point
├── index.html                           # HTML template
├── package.json                         # Dependencies
├── vite.config.js                       # Vite configuration
└── README.md                            # This file
```

## Booking Flow

The booking modal can be triggered in three ways:

### Manual Trigger
1. User clicks "Book a Table" button in Hero section

### Auto-Popup Triggers (whichever happens first)
1. **Time-based**: Modal automatically appears after 15 seconds of page visit
2. **Scroll-based**: Modal appears when user scrolls down 100px or more

The modal will only auto-show once per session to avoid annoying users.

### Booking Process
1. Modal opens with booking form
2. User enters name and phone number
3. Form validates inputs
4. On submit:
   - Generates unique UUID for the booking
   - Creates booking data object with:
     - UUID
     - Name
     - Phone number
     - Timestamp
     - Restaurant name
   - Sends POST request to dummy API endpoint
   - Shows success message with reservation ID
   - Auto-closes modal after 3 seconds

## API Integration

Currently using JSONPlaceholder as a dummy API endpoint:
```
POST https://jsonplaceholder.typicode.com/posts
```

To integrate with your own backend:
1. Replace the API URL in [BookingModal.jsx:63](src/components/BookingModal.jsx#L63)
2. Update the request payload format as needed
3. Modify error handling based on your API responses

## Customization

### Colors
Main color scheme is defined in component CSS files:
- Primary: `#ff6b35` (Orange)
- Secondary: `#f7931e` (Golden)
- Accent: `#c41e3a` (Red)

### Content
Edit the following files to customize content:
- [Hero.jsx](src/components/Hero.jsx) - Restaurant name and tagline
- [About.jsx](src/components/About.jsx) - Restaurant description and hours
- [Menu.jsx](src/components/Menu.jsx) - Menu items and prices
- [Contact.jsx](src/components/Contact.jsx) - Contact information

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

**Note:** The booking modal uses `crypto.randomUUID()` which requires a secure context (HTTPS or localhost).

## License

MIT License - Feel free to use this project for your own restaurant website!

## Contact

For questions or support, visit our restaurant or contact us at info@masalaofindia.com
