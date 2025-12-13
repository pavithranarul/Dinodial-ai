import { useState, useEffect } from 'react'
import Hero from './components/Hero'
import About from './components/About'
import Menu from './components/Menu'
import Contact from './components/Contact'
import BookingModal from './components/BookingModal'

function App() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [hasAutoShown, setHasAutoShown] = useState(false)

  const openModal = () => setIsModalOpen(true)
  const closeModal = () => {
    setIsModalOpen(false)
    // Mark as auto-shown when user closes the modal to prevent re-showing
    if (!hasAutoShown) {
      setHasAutoShown(true)
    }
  }

  useEffect(() => {
    // Don't set up listeners if modal has already been auto-shown
    if (hasAutoShown) return

    // Timer for 15 seconds
    const timer = setTimeout(() => {
      if (!isModalOpen && !hasAutoShown) {
        setIsModalOpen(true)
        setHasAutoShown(true)
      }
    }, 15000) // 15 seconds

    // Scroll detection
    const handleScroll = () => {
      if (!isModalOpen && !hasAutoShown) {
        // Show modal after user scrolls down at least 100px
        if (window.scrollY > 1000) {
          setIsModalOpen(true)
          setHasAutoShown(true)
        }
      }
    }

    window.addEventListener('scroll', handleScroll)

    // Cleanup
    return () => {
      clearTimeout(timer)
      window.removeEventListener('scroll', handleScroll)
    }
  }, [isModalOpen, hasAutoShown])

  return (
    <div className="app">
      <Hero onBookNowClick={openModal} />
      <About />
      <Menu />
      <Contact />
      <BookingModal isOpen={isModalOpen} onClose={closeModal} />
    </div>
  )
}

export default App
