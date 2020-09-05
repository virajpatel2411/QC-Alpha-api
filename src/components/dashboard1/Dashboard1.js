import React, { Component } from "react";
import axios from "axios";
import { reactLocalStorage } from "reactjs-localstorage";
import { Link } from "react-router-dom";
import {
  Table,
  Row,
  Col,
  Dropdown,
  DropdownButton,
  Form,
  Button,
  Badge,
  OverlayTrigger,
  Tooltip,
  Image,
  Modal,
} from "react-bootstrap";

import "./Dashboard1Style.css";
import saveKey from "../images/userInfoTrans.png";
import logo from "../images/QCAlphaLogoTrans.png";

class Dashboard1 extends Component {
  state = {
    showModel: false,
    apiKey: "",
    accessToken: "",
    tickerValue: "Ticker",
    expiryValue: "",
    expiryTitle: "",
    expiryListData: "",
    strikeDistanceValue: "",
    totContractsValue: "",
    dataBlocks: [],
    flag: true,
    responseData: "",
    hideColumnList: [
      false,
      false,
      false,
      false,
      false,
      false,
      false,
      false,
      false,
      false,
      false,
      false,
      false,
      false,
      false,
      false,
      false,
      false,
      false,
      false,
      false,
      false,
    ],
    totHiddenColumns: 0,
  };

  colNames = [
    { id: 1, name: "CE_OI" },
    { id: 2, name: "Vol" },
    { id: 3, name: "CE_Bid" },
    { id: 4, name: "CE_Off" },
    { id: 5, name: "CE_veg" },
    { id: 6, name: "CE_θ" },
    { id: 7, name: "CE_γ" },
    { id: 8, name: "CE_Δ" },
    { id: 9, name: "CE_IV" },
    { id: 10, name: "SynFut" },
    { id: 11, name: "Strike" },
    { id: 12, name: "Mnes" },
    { id: 13, name: "Smile" },
    { id: 14, name: "PE_IV" },
    { id: 15, name: "PE_Δ" },
    { id: 16, name: "PE_γ" },
    { id: 17, name: "PE_θ" },
    { id: 18, name: "PE_Veg" },
    { id: 19, name: "PE_Bid" },
    { id: 20, name: "PE_Off" },
    { id: 21, name: "Vol" },
    { id: 22, name: "PE_OI" },
  ];

  updateAccessToken = (event) => {
    //console.log(event.target.value)
    this.setState({
      accessToken: event.target.value,
    });
  };

  updateAPIKey = (event) => {
    this.setState({
      apiKey: event.target.value,
    });
  };

  saveAccessToken = () => {
    reactLocalStorage.set("accessToken", this.state.accessToken);
    //console.log(reactLocalStorage.get("accessToken"))
    if (
      reactLocalStorage.get("accessToken") &&
      reactLocalStorage.get("API_Key")
    ) {
      axios
        .get(
          `https://qcalpha-dashboard.herokuapp.com/instruments?accessToken=${reactLocalStorage.get(
            "accessToken"
          )}&API_Key=${reactLocalStorage.get("API_Key")}`
        )
        .then((res) => {
          console.log(res);

          let expiryList = [];

          res.data.map((val, index) =>
            expiryList.push(
              <Dropdown.Item key={index + 1} eventKey={val}>
                {val}
              </Dropdown.Item>
            )
          );

          this.setState({
            expiryListData: expiryList,
          });

          console.log(this.state.expiryListData);
        })
        .catch((err) => {
          console.log(err);
          this.setState({
            showModel: true,
          });
        });
    }
  };

  saveAPIKeys = () => {
    reactLocalStorage.set("API_Key", this.state.apiKey);

    //console.log(reactLocalStorage.get("API_Key"))

    if (
      reactLocalStorage.get("accessToken") &&
      reactLocalStorage.get("API_Key")
    ) {
      axios
        .get(
          `https://qcalpha-dashboard.herokuapp.com/instruments?accessToken=${reactLocalStorage.get(
            "accessToken"
          )}&API_Key=${reactLocalStorage.get("API_Key")}`
        )
        .then((res) => {
          console.log(res);

          let expiryList = [];

          res.data.map((val, index) =>
            expiryList.push(
              <Dropdown.Item key={index + 1} eventKey={val}>
                {val}
              </Dropdown.Item>
            )
          );

          this.setState({
            expiryListData: expiryList,
          });

          console.log(this.state.expiryListData);
        })
        .catch((err) => {
          console.log(err);
          this.setState({
            showModel: true,
          });
        });
    }
  };

  tokenKeyForm = () => {
    return (
      <Form style={{ width: "max-content", margin: "20px" }}>
        <Form.Group controlId="formAccessToken">
          <Form.Label>Access Token</Form.Label>
          <Form.Control
            placeholder="Enter Access Token"
            onChange={this.updateAccessToken}
          />
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
          <Form.Control
            type="text"
            placeholder="Enter API Key"
            onChange={this.updateAPIKey}
          />
          <Form.Text className="text-muted">
            Save API Key only once!! *Re-enter when browser cache is cleared
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

  updateTickerLabel = (event) => {
    //console.log(event);
    this.setState({
      tickerValue: event,
    });
  };

  updateExpiryLabel = (event) => {
    //let i = 0;

    /*let year='';
    while(i<4) {
      year = year + event.charAt(i);
      i=i+1;
    }

    let month = '';
    while(i<6) {
      month = month + event.charAt(i);
      i=i+1;
    }
    
    let day = '';
    while(i<8) {
      day = day + event.charAt(i);
      i=i+1;
    }

    let date = day + '-' + month + '-' + year;*/

    /*let nexpiry = "";
    i = 0;
    while (i < 4) {
      nexpiry = nexpiry + event.charAt(i);
      i = i + 1;
    }

    i = 5;
    while (i < 7) {
      nexpiry = nexpiry + event.charAt(i);
      i = i + 1;
    }

    i = 8;
    while (i < 10) {
      nexpiry = nexpiry + event.charAt(i);
      i = i + 1;
    }*/
    //console.log(nexpiry);

    this.setState({
      expiryValue: event,
      expiryTitle: event,
    });
  };

  updateStrikeDistanceLabel = (event) => {
    this.setState({
      strikeDistanceValue: event,
    });
  };

  updateTotContractsLabel = (event) => {
    this.setState({
      totContractsValue: event,
    });
  };

  contractNumbersList = () => {
    const contractNumbers = [5, 10, 15, 20];
    return (
      <div>
        {contractNumbers.map((val, index) => (
          <Dropdown.Item key={index + 1} eventKey={val}>
            {val}
          </Dropdown.Item>
        ))}
      </div>
    );
  };

  updateHideColumnList = (event, index, isHide) => {
    let newHideColumnList = this.state.hideColumnList;
    newHideColumnList[index] = isHide;

    let newTotHiddenColumns = this.state.totHiddenColumns;
    if (isHide === true) {
      newTotHiddenColumns = newTotHiddenColumns + 1;
    } else {
      newTotHiddenColumns = newTotHiddenColumns - 1;
    }

    this.setState({
      hideColumnList: newHideColumnList,
      totHiddenColumns: newTotHiddenColumns,
    });

    console.log(index, this.state.hideColumnList);

    let newdataBlocks = this.getTableData(this.state.responseData);
    this.setState({
      dataBlocks: newdataBlocks,
    });
  };

  checkHide = (index) => {
    //console.log('hide ', index, this.state.hideColumnList[index]===true)
    return this.state.hideColumnList[index] === true;
  };

  getHiddenColumns = () => {
    return (
      <div>
        {this.colNames.map((val, ind) => (
          <h5
            key={ind}
            style={{
              display: this.checkHide(ind) ? "inline-block" : "none",
              margin: "5px",
              cursor: "pointer",
            }}
            onClick={(event) => {
              this.updateHideColumnList(event, ind, false);
            }}
          >
            <Badge variant="secondary">{val.name}</Badge>
          </h5>
        ))}
      </div>
    );
  };

  checkBorderID = (outerInd, innerInd, len) => {
    if (outerInd === 1 && (innerInd === 1 || innerInd === 14)) {
      return "borderTopLeftID";
    } else if (outerInd === len && (innerInd === 1 || innerInd === 14)) {
      return "borderBottomLeftID";
    } else if (outerInd === 1 && (innerInd === 9 || innerInd === 22)) {
      return "borderTopRightID";
    } else if (outerInd === len && (innerInd === 9 || innerInd === 22)) {
      return "borderBottomRightID";
    } else if (outerInd === 1 && (innerInd <= 9 || innerInd >= 14)) {
      return "borderTopID";
    } else if (outerInd === len && (innerInd <= 9 || innerInd >= 14)) {
      return "borderBottomID";
    } else if (innerInd === 1 || innerInd === 14) {
      return "borderLeftID";
    } else if (innerInd === 9 || innerInd === 22) {
      return "borderRightID";
    }

    return null;
  };

  checkHeaderColClass = (index) => {
    if (index <= 9) {
      return "callClass";
    } else if (index >= 14) {
      return "putClass";
    } else if (index === 10) {
      return "synFutClass";
    } else if (index === 11) {
      return "strikeClass";
    } else if (index === 12) {
      return "mnesClass";
    } else if (index === 13) {
      return "smileClass";
    }

    return null;
  };

  getTableStructure = () => {
    return (
      <div>
        <Table
          striped
          bordered
          size="sm" /*className="table table-bordered table-striped"*/
        >
          <thead>
            <tr>
              {this.colNames.map((val, index) => (
                <th
                  key={index}
                  style={{
                    display: this.checkHide(val.id - 1) ? "none" : null,
                    paddingTop: "5px",
                  }}
                  className={this.checkHeaderColClass(index + 1)}
                >
                  <div
                    style={{ float: "right", cursor: "pointer" }}
                    onClick={(event) => {
                      this.updateHideColumnList(event, val.id - 1, true);
                    }}
                  >
                    <Badge variant="danger">x</Badge>
                  </div>

                  {val.name}
                </th>
              ))}
            </tr>
          </thead>
          {this.state.dataBlocks}
        </Table>
      </div>
    );
  };

  getTableData = (res) => {
    return (
      <tbody id="TableData">
        {res &&
          res.data.length > 0 &&
          Object.keys(res.data).map((outerVal, outerInd) => {
            return (
              <tr key={outerInd}>
                {Object.keys(res.data[outerVal]).map((innerVal, innerInd) => {
                  return (
                    <th
                      key={`${innerInd}-${outerInd}`}
                      style={{
                        display: this.checkHide(innerInd) ? "none" : null,
                      }}
                      className={
                        (res.data.length - 1) / 2 !== outerInd
                          ? `tableColumn-${innerInd + 1}`
                          : null
                      }
                      id={this.checkBorderID(
                        outerInd + 1,
                        innerInd + 1,
                        res.data.length
                      )}
                    >
                      {res.data[outerVal][innerVal]}
                    </th>
                  );
                })}
              </tr>
            );
          })}
      </tbody>
    );
  };

  componentDidMount = () => {
    document.title = "QCAlpha";
    //console.log(reactLocalStorage.get("accessToken"));
    if (
      reactLocalStorage.get("accessToken") &&
      reactLocalStorage.get("API_Key")
    ) {
      axios
        .get(
          `https://qcalpha-dashboard.herokuapp.com/expiry?accessToken=${reactLocalStorage.get(
            "accessToken"
          )}&API_Key=${reactLocalStorage.get("API_Key")}`
        )
        .then((res) => {
          //console.log(res);

          let expiryList = [];

          res.data.map((val, index) =>
            expiryList.push(
              <Dropdown.Item key={index + 1} eventKey={val}>
                {val}
              </Dropdown.Item>
            )
          );

          this.setState({
            expiryListData: expiryList,
          });

          //console.log(this.state.expiryListData);
        })
        .catch((err) => {
          console.log(err);
          this.setState({
            showModel: true,
          });
        });
    }
  };

  submitHandler = (event) => {
    event.preventDefault();

    clearInterval(this.interval);

    const reqData = {
      ticker: this.state.tickerValue,
      expiry: this.state.expiryValue,
      strikeDistance: this.state.strikeDistanceValue,
      totContracts: this.state.totContractsValue,
    };

    console.log("request:", reqData);

    this.interval = setInterval(() => {
      if (
        this.state.flag === true &&
        (this.state.tickerValue === "BANKNIFTY" &&
          this.state.strikeDistanceValue === "50") === false
      ) {
        this.setState({
          flag: false,
        });
        if (reactLocalStorage.get("accessToken")) {
          axios
            .get(
              `https://qcalpha-dashboard.herokuapp.com/quotes?ticker=${
                this.state.tickerValue
              }&expiry=${this.state.expiryValue}&strikeDistance=${
                this.state.strikeDistanceValue
              }&totContracts=${
                this.state.totContractsValue
              }&accessToken=${reactLocalStorage.get(
                "accessToken"
              )}&API_Key=${reactLocalStorage.get("API_Key")}`
            )
            .then((response) => {
              console.log("url post:", response);
              this.setState({
                responseData: response,
              });
              let nTable = this.getTableData(response);

              this.setState({
                dataBlocks: nTable,
                flag: true,
              });
            })
            .catch((error) => {
              console.log(error);
              this.setState({
                showModel: true,
              });
            });
        }
      }
    }, 1000);

    //console.log(this.state.dataBlocks);
  };

  renderTooltip = (props) => {
    return (
      <Tooltip id="button-tooltip" {...props}>
        Click on the Column Name to get back in the table!!
      </Tooltip>
    );
  };

  handleReload = () => {
    window.location.reload();
  };

  render() {
    return (
      <div>
        <Modal
          show={this.state.showModel}
          onHide={() => {
            this.handleReload();
          }}
          backdrop="static"
          keyboard={false}
        >
          <Modal.Header closeButton>
            <Modal.Title>Some Error Occured !!</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <ul>
              <li>
                Ensure all neccessary input values are selected (e.g. Ticker,
                Expiry etc.)
              </li>
              <li>Re-enter value of API Key and latest Access Token.</li>
              <DropdownButton title="Input Access Token and API Key">
                {this.tokenKeyForm()}
              </DropdownButton>
              <li>Ensure Stable Internet Connection</li>
              <li>
                {" "}
                May some service is temporarily unavailable/down so try after
                some time
              </li>
            </ul>
          </Modal.Body>
          <Modal.Footer>
            <Button
              variant="secondary"
              onClick={() => {
                this.handleReload();
              }}
            >
              Reload the page
            </Button>
          </Modal.Footer>
        </Modal>

        <nav className="navbar navbar-expand navbar-dark bg-dark sticky-top">
          <div className="container-fluid">
            <Link className="navbar-brand" to="/">
              <Image src={logo} className="NavbarImage" /> QCAlpha
            </Link>

            <Dropdown>
              <Dropdown.Toggle
                style={{
                  borderRadius: "10%",
                  padding: "3px",
                  background: "#eee",
                  border: "0px",
                }}
              >
                <Image src={saveKey} className="NavbarImage" />
              </Dropdown.Toggle>
              <Dropdown.Menu>{this.tokenKeyForm()}</Dropdown.Menu>
            </Dropdown>
          </div>
        </nav>

        <div className="container containerOption">
          <form onSubmit={this.submitHandler}>
            <Row>
              <Col>
                <DropdownButton
                  id="tickerDropdownMenu"
                  title={this.state.tickerValue}
                  onSelect={this.updateTickerLabel}
                >
                  <Dropdown.Item eventKey="NIFTY">NIFTY</Dropdown.Item>
                  <Dropdown.Item eventKey="BANKNIFTY">BANKNIFTY</Dropdown.Item>
                </DropdownButton>
              </Col>

              <Col>
                <DropdownButton
                  id="expiryDropdownMenu"
                  title={`Expiry - ${this.state.expiryTitle}`}
                  onSelect={this.updateExpiryLabel}
                >
                  {this.state.expiryListData}
                </DropdownButton>
              </Col>

              <Col>
                <DropdownButton
                  id="strikeDistanceDropdownMenu"
                  title={`Strike distance - ${this.state.strikeDistanceValue}`}
                  onSelect={this.updateStrikeDistanceLabel}
                >
                  <Dropdown.Item
                    eventKey="50"
                    //disabled={this.state.tickerValue==='BANKNIFTY'}
                    style={{
                      display:
                        this.state.tickerValue === "BANKNIFTY"
                          ? "none"
                          : "block",
                    }}
                  >
                    50
                  </Dropdown.Item>
                  <Dropdown.Item eventKey="100">100</Dropdown.Item>
                  <Dropdown.Item eventKey="500">500</Dropdown.Item>
                </DropdownButton>
              </Col>

              <Col>
                <DropdownButton
                  id="totContractsDropdownMenu"
                  title={`No. of Contracts - ${this.state.totContractsValue}`}
                  onSelect={this.updateTotContractsLabel}
                >
                  {this.contractNumbersList()}
                </DropdownButton>
              </Col>

              <Col>
                <Button type="submit" variant="success">
                  {" "}
                  Show{" "}
                </Button>
              </Col>
            </Row>
          </form>
        </div>

        <div
          style={{
            display: this.state.totHiddenColumns === 0 ? "none" : null,
            margin: "10px",
            border: "5px solid darkslategrey",
            borderRadius: "15px",
            background: "#fff",
          }}
        >
          <h5>
            Hidden Columns{" "}
            <OverlayTrigger
              placement="right"
              overlay={
                <Tooltip id="tooltip-hide-cols">
                  Click on the Column Name to get back in the table!!
                </Tooltip>
              }
            >
              <Badge variant="info" style={{ display: "inline" }}>
                𝒊
              </Badge>
            </OverlayTrigger>
          </h5>
          {this.getHiddenColumns()}
        </div>

        <div className="container containerTable">
          <div className="table-responsive">{this.getTableStructure()}</div>
        </div>
      </div>
    );
  }
}

export default Dashboard1;
