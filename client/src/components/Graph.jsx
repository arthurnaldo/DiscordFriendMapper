import React, { useState, useEffect } from 'react';
import '../Graph.css';
import { getServers, updateGraph, getGraphUrl } from '../api';

function Graph() {
    const [servers, setServers] = useState([]);
    const [selectedServer, setSelectedServer] = useState(null);
    const [graphUrl, setGraphUrl] = useState('');
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
  
    useEffect(() => {
      const fetchServers = async () => {
        setLoading(true);
        try {
          const serverList = await getServers();
          setServers(serverList);
        } catch (err) {
          setError('Failed to load servers. Please try again.');
        } finally {
          setLoading(false);
        }
      };
      fetchServers();
    }, []);
  
    const handleServerSelect = (serverName) => {
      setSelectedServer(serverName);
      setGraphUrl(getGraphUrl(serverName)); // Set the URL of the graph
      setIsDropdownOpen(false); // Close the dropdown after selection
    };
  
    const handleDropdownToggle = () => {
      setIsDropdownOpen(!isDropdownOpen);
    };
  
    const handleUpdateGraph = async () => {
      if (selectedServer) {
        try {
          const res = await updateGraph(selectedServer);
          alert(res.message);
        } catch (err) {
          setError('Failed to update the graph. Please try again.');
        }
      }
    };
  
    return (
      <div className="app-container">
        <h1 className="title">Discord Interaction Graph</h1>
  
        <p className="description">
          This app allows you to view and update interaction graphs for your Discord servers. 
          Select a server from the dropdown and click "Update Graph" to generate the interaction graph.
        </p>
  
        <div className="server-selection">
          <label className="label">Select a Server:</label>
          <div className="dropdown" onClick={handleDropdownToggle}>
            <div className="dropdown-selected">
              {selectedServer || '--Choose a server--'}
            </div>
            {isDropdownOpen && (
              <ul className="dropdown-list">
                {servers.map((server) => (
                  <li
                    key={server}
                    className="dropdown-item"
                    onClick={() => handleServerSelect(server)}
                  >
                    {server}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
  
        {loading && <p className="loading">Loading servers...</p>}
  
        <button className="update-button" onClick={handleUpdateGraph} disabled={!selectedServer}>
          Update Graph
        </button>
  
        {error && <p className="error">{error}</p>}
  
        {graphUrl && (
          <div className="graph-container">
            <h2 className="graph-title">Graph for {selectedServer}</h2>
            <iframe
              className="graph-iframe"
              src={graphUrl}
              title="Interaction Graph"
            />
          </div>
        )}
      </div>
    );
  }

export default Graph;