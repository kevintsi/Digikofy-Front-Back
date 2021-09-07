import React from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route
} from "react-router-dom";
import Register from "./components/Register/Register"
import Login from "./components/Login/Login"
import Home from "./components/Home/Home"
import DetailCoffee from "./components/DetailCoffee/DetailCoffee"

export default function Routes() {
  return (
    <Router>
        {/* A <Switch> looks through its children <Route>s and
            renders the first one that matches the current URL. */}
        <Switch>
          <Route path="/register">
            <Register />
          </Route>
          <Route path="/login">
            <Login />
          </Route>
          <Route path="/home">
            <Home />
          </Route>
          <Route path="/detail/:id">
            <DetailCoffee />
          </Route>
        </Switch>
    </Router>
  );
}