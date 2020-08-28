import React, { Component } from 'react';
import { Link } from "react-router-dom";
import { reactLocalStorage } from "reactjs-localstorage";
import {Image, Dropdown, Row, Col, Form, Button} from "react-bootstrap";

import "./HomeStyle.css";
import logo from "./images/QCAlphaLogoTrans.png";
import saveKey from "./images/userInfoTrans.png";

class Home extends Component {

  state = {
    accessToken: "",
    apiKey: "",
  }

  componentDidMount = () => {
    document.title="QCAlpha";
  }

  updateAccessToken = (event) => {
    this.setState({
      accessToken: event.target.value,
    });
  };

  updateAPIKey = (event) => {
    this.setState({
      apiKey: event.target.value,
    })
  };

  saveAccessToken = () => {
    reactLocalStorage.set("accessToken", this.state.accessToken);
  };

  saveAPIKeys = () => {
    reactLocalStorage.set("API_Key", this.state.apiKey);
  }

  tokenKeyForm = () => {
    return (
      <Form style={{width: 'max-content', margin: '20px'}}>
        
        <Form.Group controlId="formAccessToken">
          <Form.Label>Access Token</Form.Label>
          <Form.Control placeholder="Enter Access Token" onChange={this.updateAccessToken}/>
          <Form.Text className="text-muted">
            Save Access Token once in a Day...
          </Form.Text>
        </Form.Group>

        <Form.Group as={Row}>
          <Col sm={{ span: 12, offset: 3 }}>
            <Button variant="success" onClick={this.saveAccessToken}>
              Save Access Token
            </Button>
          </Col>
        </Form.Group>
        
        <Form.Group as={Col} controlId="formAPIKey">
          <Form.Label>API Key</Form.Label>
          <Form.Control type="text" placeholder="Enter API Key" onChange={this.updateAPIKey}/>
          <Form.Text className="text-muted">
            Save API Key only once!!
            *Re-enter when browser cache is cleared
          </Form.Text>
        </Form.Group>

        <Form.Group as={Row}>
          <Col sm={{ span: 12, offset: 4 }}>
            <Button variant="success" onClick={this.saveAPIKeys}>
              Save API Key
            </Button>
          </Col>
        </Form.Group>

      </Form>
    );
  };

  render() {
    return (
      <div>
        <nav className="navbar navbar-expand navbar-dark bg-dark sticky-top">
          <div className="container-fluid">
            <Link className="navbar-brand" to="/">
              <Image src={logo} className="NavbarImage"/>{" "}QCAlpha
            </Link>
            
            <Dropdown>
              <Dropdown.Toggle style={{borderRadius: '10%', padding: '3px', background: '#eee', border: '0px'}}>
                <Image src={saveKey} className="NavbarImage"/>
              </Dropdown.Toggle>
              <Dropdown.Menu>
                {this.tokenKeyForm()}
              </Dropdown.Menu>
            </Dropdown>
          </div> 
        </nav>

        <div className="container CenterHome">
          <div>
              <Image src={logo} className="ImageHome"/>
              <p className="TitleHome">QCAlpha Adviser</p>
          </div>

          <div  className="PrimaryButton">
            Market Watch
            <Link to="/marketwatch_dashboard"
                  className="stretched-link"
            />
          </div>
          <div  className="PrimaryButton">
            Strategies
            <Link to="/strategies_dashboard"
                  className="stretched-link"
            />
          </div>

        </div>
      </div>
    )
  }
}

export default Home;
