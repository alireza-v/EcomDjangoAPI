import React, { useEffect, useState } from "react";
import axios from "axios";

const CategoryTree = ({ category }) => {
  return (
    <div className="category-tree" style={{ marginLeft: "1rem", borderLeft: "1px solid #ccc", paddingLeft: "1rem" }}>
      <h4>{category.title}</h4>

      {category.products && category.products.length > 0 && (
        <ul>
          {category.products.map((product, index) => (
            <li key={`product-${index}`}>
              {product.name} - ${product.price}
            </li>
          ))}
        </ul>
      )}

      {category.subcategories && category.subcategories.length > 0 && (
        <div>
          {category.subcategories.map((sub, index) => (
            <CategoryTree key={`subcat-${sub.title}-${index}`} category={sub} />
          ))}
        </div>
      )}
    </div>
  );
};

const CategoryList = () => {
  const [categories, setCategories] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    document.title = "Products";
    const fetchCategories = async () => {
      try {
        const { data } = await axios.get("http://localhost:9000/products/", {
          headers: {
            Authorization:`Token ${localStorage.getItem('auth_token')}`
          }
        });
        setCategories(data);
        setError(null);
      } catch (error) {
        if (error.response?.status === 429) {
          setError("Too many requests. Please try again later.");
        } else {
          setError("An unknown error occurred.");
        }
      }
    };
    fetchCategories();
  }, []);

  return (
    <div className="category-list">
      <h2>Subcategories</h2>
      {error && <div className="error-message">{error}</div>}
      {categories.map((category, index) => (
        <div key={`cat-${category.title}-${index}`}>
          <CategoryTree category={category} />
        </div>
      ))}
    </div>
  );
};

export default CategoryList;
