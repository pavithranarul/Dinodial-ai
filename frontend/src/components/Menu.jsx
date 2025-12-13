import './Menu.css'

function Menu() {
  const menuItems = [
    {
      id: 1,
      name: 'Butter Chicken',
      description: 'Tender chicken in a rich, creamy tomato sauce',
      price: '$16.99',
      category: 'Main Course'
    },
    {
      id: 2,
      name: 'Biryani',
      description: 'Aromatic basmati rice with spices and your choice of protein',
      price: '$14.99',
      category: 'Main Course'
    },
    {
      id: 3,
      name: 'Samosa',
      description: 'Crispy pastry filled with spiced potatoes and peas',
      price: '$6.99',
      category: 'Appetizer'
    },
    {
      id: 4,
      name: 'Paneer Tikka',
      description: 'Grilled cottage cheese marinated in spices',
      price: '$12.99',
      category: 'Appetizer'
    },
    {
      id: 5,
      name: 'Tandoori Chicken',
      description: 'Chicken marinated in yogurt and spices, cooked in tandoor',
      price: '$15.99',
      category: 'Main Course'
    },
    {
      id: 6,
      name: 'Naan',
      description: 'Traditional Indian flatbread baked in tandoor',
      price: '$3.99',
      category: 'Bread'
    },
    {
      id: 7,
      name: 'Gulab Jamun',
      description: 'Sweet dumplings soaked in rose-flavored syrup',
      price: '$5.99',
      category: 'Dessert'
    },
    {
      id: 8,
      name: 'Palak Paneer',
      description: 'Cottage cheese cubes in creamy spinach curry',
      price: '$13.99',
      category: 'Main Course'
    }
  ]

  return (
    <section className="menu" id="menu">
      <div className="container">
        <h2 className="section-title">Our Signature Dishes</h2>
        <p className="menu-intro">
          Explore our carefully curated menu featuring authentic Indian delicacies
        </p>
        <div className="menu-grid">
          {menuItems.map(item => (
            <div key={item.id} className="menu-item">
              <div className="menu-item-header">
                <h3>{item.name}</h3>
                <span className="price">{item.price}</span>
              </div>
              <p className="category">{item.category}</p>
              <p className="description">{item.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default Menu
