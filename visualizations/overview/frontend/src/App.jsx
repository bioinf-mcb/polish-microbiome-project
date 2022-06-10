import { Routes, Route, Navigate } from 'react-router-dom';
import React, { Suspense, lazy } from "react";
import MainContainer from './Components/MainContainer';
import PatientsInspector from './pages/PatientsInspector';
import './App.css';

require('dotenv').config()


function App() {
  return (
    <Suspense fallback={<MainContainer />}>
      <Routes>
        <Route path="/" element={<MainContainer />}>
          <Route path="" element={<Navigate to="/inspector/1" />} />
          <Route path="inspector/:patient_id" element={<PatientsInspector />} />
        </Route>
      </Routes>
    </Suspense>
  );
}

export default App;
