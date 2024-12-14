import React, { useState, useEffect } from 'react';
import { getServers, updateGraph, getGraphUrl } from './api';
import './App.css';
import './components/Graph.jsx'
import Graph from './components/Graph.jsx';

function App() {
  return (
    <Graph />
  )
}

export default App;
