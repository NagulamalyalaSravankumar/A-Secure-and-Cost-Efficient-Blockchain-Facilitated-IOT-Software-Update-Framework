pragma solidity >= 0.8.11 <= 0.8.11;

contract SoftwareUpdate {
    string public owner_manufacturer;
    string public software_updates;
    string public payments;
      
    //save owner and manufacturer details	
    function setUser(string memory om) public {
       owner_manufacturer = om;	
    }
   //get owner and manufacturer details
    function getUser() public view returns (string memory) {
        return owner_manufacturer;
    }
    //add encrypted software updates blocks to blockchain
    function setsoftwareUpdates(string memory su) public {
       software_updates = su;	
    }
    //get software updates
    function getsoftwareUpdates() public view returns (string memory) {
        return software_updates;
    }

    //add payments details to blockchain
    function setPayments(string memory p) public {
       payments = p;	
    }
    //get payment details
    function getPayments() public view returns (string memory) {
        return payments;
    }

    constructor() public {
        owner_manufacturer = "";
	software_updates="";
	payments="";
    }
}