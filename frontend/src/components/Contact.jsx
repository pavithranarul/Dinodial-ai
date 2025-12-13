import './Contact.css'

function Contact() {
  return (
    <section className="contact" id="contact">
      <div className="container">
        <h2 className="section-title">Visit Us</h2>
        <div className="contact-content">
          <div className="contact-info">
            <div className="info-item">
              <div className="info-icon">📍</div>
              <div>
                <h4>Address</h4>
                <p>123 Spice Street, Curry Lane</p>
                <p>New Delhi, India 110001</p>
              </div>
            </div>
            <div className="info-item">
              <div className="info-icon">📞</div>
              <div>
                <h4>Phone</h4>
                <p>+1 (555) 123-4567</p>
                <p>+1 (555) 765-4321</p>
              </div>
            </div>
            <div className="info-item">
              <div className="info-icon">✉️</div>
              <div>
                <h4>Email</h4>
                <p>info@masalaofindia.com</p>
                <p>reservations@masalaofindia.com</p>
              </div>
            </div>
            <div className="info-item">
              <div className="info-icon">🕒</div>
              <div>
                <h4>Hours</h4>
                <p>Mon-Fri: 11:00 AM - 10:00 PM</p>
                <p>Sat-Sun: 12:00 PM - 11:00 PM</p>
              </div>
            </div>
          </div>
          <div className="contact-map">
            <div className="map-placeholder">
              <p>🗺️</p>
              <p>Map Location</p>
            </div>
          </div>
        </div>
        <div className="social-links">
          <h3>Follow Us</h3>
          <div className="social-icons">
            <a href="#" className="social-icon">Facebook</a>
            <a href="#" className="social-icon">Instagram</a>
            <a href="#" className="social-icon">Twitter</a>
            <a href="#" className="social-icon">YouTube</a>
          </div>
        </div>
      </div>
      <footer className="footer">
        <p>&copy; 2024 Masala of India. All rights reserved.</p>
      </footer>
    </section>
  )
}

export default Contact
