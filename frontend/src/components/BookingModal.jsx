import { useState } from 'react'
import './BookingModal.css'

function BookingModal({ isOpen, onClose }) {
  const [formData, setFormData] = useState({
    name: '',
    phoneNumber: ''
  })
  const [errors, setErrors] = useState({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitStatus, setSubmitStatus] = useState(null)

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }))
    }
  }

  const validateForm = () => {
    const newErrors = {}

    // Validate name
    if (!formData.name.trim()) {
      newErrors.name = 'Name is required'
    } else if (formData.name.trim().length < 2) {
      newErrors.name = 'Name must be at least 2 characters'
    }

    // Validate phone number
    if (!formData.phoneNumber.trim()) {
      newErrors.phoneNumber = 'Phone number is required'
    } else if (!/^[\d\s\-\+\(\)]{10,}$/.test(formData.phoneNumber)) {
      newErrors.phoneNumber = 'Please enter a valid phone number'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    setIsSubmitting(true)
    setSubmitStatus(null)

    try {
      // Generate customer_id in format RESXXXXX (RES + 5 digits)
      const randomDigits = Math.floor(10000 + Math.random() * 90000) // Generates 5-digit number
      const customerId = `RES${randomDigits}`

      // Prepare booking data
      const bookingData = {
        name: formData.name.trim(),
        mobile: formData.phoneNumber.trim(),
        customer_id: customerId,
        timestamp: new Date().toISOString()
      }

      console.log('Booking Data:', bookingData)

      // Send to dummy API
      const response = await fetch('https://dc08a33d7c1c.ngrok-free.app/customer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(bookingData)
      })

      if (!response.ok) {
        throw new Error('Booking failed')
      }

      const result = await response.json()
      console.log('API Response:', result)

      // Show success message
      setSubmitStatus({
        type: 'success',
        message: `Thanks for your interest!.`
      })

      // Reset form after 3 seconds and close modal
      setTimeout(() => {
        setFormData({ name: '', phoneNumber: '' })
        setSubmitStatus(null)
        onClose()
      }, 3000)

    } catch (error) {
      console.error('Booking error:', error)
      setSubmitStatus({
        type: 'error',
        message: 'Sorry, something went wrong. Please try again or call us directly.'
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleClose = () => {
    if (!isSubmitting) {
      setFormData({ name: '', phoneNumber: '' })
      setErrors({})
      setSubmitStatus(null)
      onClose()
    }
  }

  if (!isOpen) return null

  return (
    <div className="modal-overlay" onClick={handleClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={handleClose} disabled={isSubmitting}>
          &times;
        </button>

        <h2 className="modal-title">Reserve Your Table</h2>
        <p className="modal-subtitle">Book your dining experience at Masala of India</p>

        <form onSubmit={handleSubmit} className="booking-form">
          <div className="form-group">
            <label htmlFor="name">Full Name *</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              className={errors.name ? 'error' : ''}
              placeholder="Enter your full name"
              disabled={isSubmitting}
            />
            {errors.name && <span className="error-message">{errors.name}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="phoneNumber">Phone Number *</label>
            <input
              type="tel"
              id="phoneNumber"
              name="phoneNumber"
              value={formData.phoneNumber}
              onChange={handleChange}
              className={errors.phoneNumber ? 'error' : ''}
              placeholder="Enter your phone number"
              disabled={isSubmitting}
            />
            {errors.phoneNumber && <span className="error-message">{errors.phoneNumber}</span>}
          </div>

          {submitStatus && (
            <div className={`status-message ${submitStatus.type}`}>
              {submitStatus.type === 'success' ? '✓ ' : '✗ '}
              {submitStatus.message}
            </div>
          )}

          <button
            type="submit"
            className="submit-button"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Booking...' : 'Confirm Reservation'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default BookingModal
