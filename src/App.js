import React from 'react';
import { BrowserRouter, Switch, Route } from "react-router-dom";

import Home from './components/Home.js';
import Dashboard1 from './components/dashboard1/Dashboard1.js';
import Dashboard2 from './components/dashboard2/Dashboard2.js';

import './App.css';

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <link
          rel="stylesheet"
          href="https://maxcdn.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css"
          integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T"
          crossOrigin="anonymous"
        />
        <Switch>
          <Route exact path="/" component={Home} />
          <Route exact path="/marketwatch_dashboard" component={Dashboard1} />
          <Route exact path="/strategies_dashboard" component={Dashboard2} />
        </Switch>
      </div>
    </BrowserRouter>
  );
}

export default App;
