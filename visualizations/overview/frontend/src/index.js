import React from 'react';
import 'mdb-react-ui-kit/dist/css/mdb.min.css'
import App from './App';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Route, Routes } from "react-router-dom";
import './index.css';

var root = createRoot(document.getElementById('root'));
root.render(
    <React.Fragment>
      <BrowserRouter history={history}>
          <Routes>
            <Route path="/*" element={<App />} />
          </Routes>
      </BrowserRouter>
    </React.Fragment>
  );
  
