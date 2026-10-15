import React from 'react';
import { createRoot } from 'react-dom/client';
import Posters from './Posters.jsx';
import '../base.css';
import './posters.css';

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Posters />
  </React.StrictMode>
);
