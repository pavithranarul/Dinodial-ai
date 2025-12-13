import './Hero.css'

function Hero({ onBookNowClick }) {
  return (
    <section className="hero">
      <div className="hero-overlay"></div>
      <div className="hero-content">
        <h1 className="hero-title">Masala of India</h1>
        <p className="hero-subtitle">Authentic Indian Flavors in Every Bite</p>
        <p className="hero-description">
          Experience the rich and aromatic cuisine of India with traditional recipes
          passed down through generations
        </p>
        <button className="cta-button" onClick={onBookNowClick}>
          Book a Table
        </button>
      </div>
    </section>
  )
}

export default Hero
