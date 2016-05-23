/*
This file is part of the DAO.

The DAO is free software: you can redistribute it and/or modify
it under the terms of the GNU lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

The DAO is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU lesser General Public License for more details.

You should have received a copy of the GNU lesser General Public License
along with the DAO.  If not, see <http://www.gnu.org/licenses/>.
*/


/*
Sample Proposal from a Contractor to the DAO.
Feel free to use as a template for your own proposal.
*/

import "./DAO.sol";

contract SampleOffer {

    uint public totalCosts;
    uint public oneTimeCosts;
    uint public dailyWithdrawLimit;

    address public contractor;
    bytes32 public IPFSHashOfTheProposalDocument;
    uint public minDailyWithdrawLimit;
    uint public paidOut;

    uint public dateOfSignature;
    DAO public client; // address of DAO
    DAO public originalClient; // address of DAO who signed the contract
    bool public isContractValid;

    uint public rewardDivisor;
    uint public deploymentReward;

    modifier onlyClient {
        if (msg.sender != address(client))
            throw;
        _
    }

    // Prevents methods from perfoming any value transfer
    modifier noEther() {if (msg.value > 0) throw; _}

    function SampleOffer(
        address _contractor,
        address _client,
        bytes32 _IPFSHashOfTheProposalDocument,
        uint _totalCosts,
        uint _oneTimeCosts,
        uint _minDailyWithdrawLimit
    ) {
        contractor = _contractor;
        originalClient = DAO(_client);
        client = DAO(_client);
        IPFSHashOfTheProposalDocument = _IPFSHashOfTheProposalDocument;
        totalCosts = _totalCosts;
        oneTimeCosts = _oneTimeCosts;
        minDailyWithdrawLimit = _minDailyWithdrawLimit;
        dailyWithdrawLimit = _minDailyWithdrawLimit;
    }

    function sign() {
        if (msg.sender != address(originalClient) // no good samaritans give us money
            || msg.value != totalCosts    // no under/over payment
            || dateOfSignature != 0)      // don't sign twice
            throw;
        if (!contractor.send(oneTimeCosts))
            throw;
        dateOfSignature = now;
        isContractValid = true;
    }

    function setDailyWithdrawLimit(uint _dailyWithdrawLimit) onlyClient noEther {
        if (_dailyWithdrawLimit >= minDailyWithdrawLimit)
            dailyWithdrawLimit = _dailyWithdrawLimit;
    }

    // "fire the contractor"
    function returnRemainingEther() onlyClient {
        if (client.DAOrewardAccount().call.value(this.balance)())
            isContractValid = false;
    }

    function getDailyPayment() {
        if (msg.sender != contractor)
            throw;
        uint amount = (now - dateOfSignature + 1 days) / (1 days) * dailyWithdrawLimit - paidOut;
        if (contractor.send(amount))
            paidOut += amount;
    }

    function setRewardDivisor(uint _rewardDivisor) onlyClient noEther {
        rewardDivisor = _rewardDivisor;
    }

    function setDeploymentReward(uint _deploymentReward) onlyClient noEther {
        deploymentReward = _deploymentReward;
    }

    function updateClientAddress(DAO _newClient) onlyClient noEther {
        client = _newClient;
    }

    function () {
        throw; // this is a business contract, no donations
    }

    // interface for Ethereum Computer
    function payOneTimeReward() returns(bool) {
        // client DAO should not be able to pay itself generating
        // "free" reward tokens
        if (msg.sender == address(client))
            throw;

        if (msg.value < deploymentReward)
            throw;

        if (originalClient.DAOrewardAccount().call.value(msg.value)()) {
            return true;
        } else {
            throw;
        }
    }

    // pay reward
    function payReward() returns(bool) {
        // client DAO should not be able to pay itself generating
        // "free" reward tokens
        if (msg.sender == address(client))
            throw;

        if (originalClient.DAOrewardAccount().call.value(msg.value)()) {
            return true;
        } else {
            throw;
        }
    }
}
