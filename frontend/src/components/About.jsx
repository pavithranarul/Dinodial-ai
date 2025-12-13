import './About.css'

function About() {
  return (
    <section className="about" id="about">
      <div className="container">
        <h2 className="section-title">About Our Restaurant</h2>
        <div className="about-content">
          <div className="about-text">
            <h3>A Journey Through Indian Cuisine</h3>
            <p>
              Welcome to Masala of India, where we bring you the authentic flavors
              of India with recipes that have been cherished for generations. Our
              master chefs use only the finest ingredients and traditional cooking
              methods to create dishes that transport you straight to the heart of India.
            </p>
            <p>
              From the aromatic biryanis to the creamy butter chicken, from the tangy
              chaats to the sweet gulab jamun, every dish tells a story of rich
              heritage and culinary excellence.
            </p>
            <div className="hours">
              <h4>Opening Hours</h4>
              <p><strong>Monday - Friday:</strong> 11:00 AM - 10:00 PM</p>
              <p><strong>Saturday - Sunday:</strong> 12:00 PM - 11:00 PM</p>
            </div>
          </div>
          <div className="about-features">
            <div className="feature">
              <div className="feature-icon">🍛</div>
              <h4>Authentic Recipes</h4>
              <p>Traditional recipes passed down through generations</p>
            </div>
            <div className="feature">
              <div className="feature-icon">👨‍🍳</div>
              <h4>Expert Chefs</h4>
              <p>Master chefs with decades of experience</p>
            </div>
            <div className="feature">
              <div className="feature-icon">🌶️</div>
              <h4>Fresh Spices</h4>
              <p>Imported spices for authentic flavors</p>
            </div>
            <div className="feature">
              <div className="feature-icon">⭐</div>
              <h4>Quality Service</h4>
              <p>Warm hospitality and excellent service</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

export default About
