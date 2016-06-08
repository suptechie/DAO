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
  An Offer from a Contractor to the DAO without any reward going back to
  the DAO.

  Feel free to use as a template for your own proposal.

  Actors:
  - Offerer:    the entity that creates the Offer. Usually it is the initial
                Contractor.
  - Contractor: the entity that has rights to withdraw ether to perform
                its project.
  - Client:     the DAO that gives ether to the Contractor. It signs off
                the Offer, can adjust daily withdraw limit or even fire the
                Contractor.

  -- Important Note For Compilation --
  This contract also reads from the DAO's proposal struct array. There used to
  be a solidity bug (https://github.com/ethereum/solidity/issues/598#issuecomment-224015639)
  that is now fixed which would result in wrong values when reading from the
  proposals array.

  Use a solc that includes commit:  0a0fc04641787ce057a9fcc9e366ea898b1fd8d6
  to be sure that the contract is compiled with the fix and that the proposals
  member attributes are read correctly. This comment will be updated as soon
  as the fix makes it into a solc release.
*/

import "./DAO.sol";

contract PFOffer {

    // Period of time after which money can be withdrawn from this contract
    uint constant payoutFreezePeriod = 3 weeks;
    // Time before the end of the voting period after which
    // checkVoteStatus() can no longer be called
    uint constant voteStatusDeadline = 48 hours;

    // The total cost of the Offer. Exactly this amount is transfered from the
    // Client to the Offer contract when the Offer is signed by the Client.
    // Set once by the Offerer.
    uint totalCosts;

    // Initial withdraw to the Contractor. It is done the moment the Offer is
    // signed.
    // Set once by the Offerer.
    uint oneTimeCosts;
    bool oneTimeCostsPaid;

    // The minimal daily withdraw limit that the Contractor accepts.
    // Set once by the Offerer.
    uint128 minDailyWithdrawLimit;

    // The amount of wei the Contractor has right to withdraw daily above the
    // initial withdraw. The Contractor does not have to do the withdraws every
    // day as this amount accumulates.
    uint128 dailyWithdrawLimit;

    // The address of the Contractor.
    address contractor;

    // The hash of the Proposal/Offer document.
    bytes32 hashOfTheProposalDocument;

    // The time of the last withdraw to the Contractor.
    uint lastPayment;

    uint dateOfSignature;
    DAO client; // address of DAO
    DAO originalClient; // address of DAO who signed the contract
    bool isContractValid;
    uint proposalID;
    bool wasApprovedBeforeDeadline;

    modifier onlyClient {
        if (msg.sender != address(client))
            throw;
        _
    }
    modifier onlyContractor {
        if (msg.sender != address(contractor))
            throw;
        _
    }

    // Prevents methods from perfoming any value transfer
    modifier noEther() {if (msg.value > 0) throw; _}

    function PFOffer(
        address _contractor,
        address _client,
        bytes32 _hashOfTheProposalDocument,
        uint _totalCosts,
        uint _oneTimeCosts,
        uint128 _minDailyWithdrawLimit
    ) {
        contractor = _contractor;
        originalClient = DAO(_client);
        client = DAO(_client);
        hashOfTheProposalDocument = _hashOfTheProposalDocument;
        totalCosts = _totalCosts;
        oneTimeCosts = _oneTimeCosts;
        minDailyWithdrawLimit = _minDailyWithdrawLimit;
        dailyWithdrawLimit = _minDailyWithdrawLimit;
    }

    // non-value-transfer getters
    function getTotalCosts() noEther constant returns (uint) {
        return totalCosts;
    }

    function getOneTimeCosts() noEther constant returns (uint) {
        return oneTimeCosts;
    }

    function getMinDailyWithdrawLimit() noEther constant returns (uint128) {
        return minDailyWithdrawLimit;
    }

    function getDailyWithdrawLimit() noEther constant returns (uint128) {
        return dailyWithdrawLimit;
    }

    function getContractor() noEther constant returns (address) {
        return contractor;
    }

    function getHashOfTheProposalDocument() noEther constant returns (bytes32) {
        return hashOfTheProposalDocument;
    }

    function getLastPayment() noEther constant returns (uint) {
        return lastPayment;
    }

    function getDateOfSignature() noEther constant returns (uint) {
        return dateOfSignature;
    }

    function getClient() noEther constant returns (DAO) {
        return client;
    }

    function getOriginalClient() noEther constant returns (DAO) {
        return originalClient;
    }

    function getIsContractValid() noEther constant returns (bool) {
        return isContractValid;
    }

    function getOneTimeCostsPaid() noEther constant returns (bool) {
        return oneTimeCostsPaid;
    }

    function getWasApprovedBeforeDeadline() noEther constant returns (bool) {
        return wasApprovedBeforeDeadline;
    }

    function getProposalID() noEther constant returns (uint) {
        return proposalID;
    }

    function sign() {
        var (_,,,votingDeadline,,) = client.proposals(proposalID);
        if (msg.sender != address(originalClient) // no good samaritans give us ether
            || msg.value != totalCosts    // no under/over payment
            || dateOfSignature != 0       // don't sign twice
            || !wasApprovedBeforeDeadline // fail if the voteStatusCheck was not done
            || now < votingDeadline + 3 days)
            throw;

        dateOfSignature = now;
        isContractValid = true;
        lastPayment = now + payoutFreezePeriod;
    }

    function setDailyWithdrawLimit(uint128 _dailyWithdrawLimit) onlyClient noEther {
        if (_dailyWithdrawLimit >= minDailyWithdrawLimit)
            dailyWithdrawLimit = _dailyWithdrawLimit;
    }

    // "fire the contractor"
    function returnRemainingEther() noEther onlyClient {
        if (originalClient.DAOrewardAccount().call.value(this.balance)())
            isContractValid = false;
    }

    // Withdraw to the Contractor.
    //
    // Withdraw the amount of ether the Contractor has right to according to
    // the current withdraw limit.
    // Executing this function before the Offer is signed off by the Client
    // makes no sense as this contract has no ether.
    function getDailyPayment() noEther {
        if (msg.sender != contractor || now < dateOfSignature + payoutFreezePeriod)
            throw;
        uint timeSinceLastPayment = now - lastPayment;
        // Calculate the amount using 1 second precision.
        uint amount = (timeSinceLastPayment * dailyWithdrawLimit) / (1 days);
        if (amount > this.balance) {
            amount = this.balance;
        }
        if (contractor.send(amount))
            lastPayment = now;
    }

    function getOneTimePayment() noEther {
        if (msg.sender != contractor
            || now < dateOfSignature + payoutFreezePeriod
            || oneTimeCostsPaid ) {
            throw;
        }

        if (!contractor.send(oneTimeCosts))
            throw;

        oneTimeCostsPaid = true;
    }

    // Once a proposal is submitted, the Contractor should call this
    // function to register its proposal ID with the offer contract
    // so that the vote can be watched and checked with `checkVoteStatus()`
    function watchProposal(uint _proposalID) noEther onlyContractor {
        var (recipient,,,votingDeadline,open,) = client.proposals(_proposalID);
        if (recipient == address(this)
            && votingDeadline > now
            && open
            && proposalID == 0) {
           proposalID =  _proposalID;
        }
    }

    // The proposal will not accept the results of the vote if it wasn't able
    // to be sure that YEA was able to succeed 48 hours before the deadline
    function checkVoteStatus() noEther {
        var (,,,votingDeadline,,,,,,yea,nay,) = client.proposals(proposalID);
        uint quorum = yea * 100 / client.totalSupply();

        // Only execute until 48 hours before the deadline
        if (now > votingDeadline - voteStatusDeadline) {
            throw;
        }
        // If quorum is met and majority is for it then the prevote
        // check can be considered as succesfull
        wasApprovedBeforeDeadline = (quorum >= 100 / client.minQuorumDivisor() && yea > nay);
    }

    // Change the client DAO by giving the new DAO's address
    // warning: The new DAO must come either from a split of the original
    // DAO or an update via `newContract()` so that it can claim rewards
    function updateClientAddress(DAO _newClient) onlyClient noEther {
        client = _newClient;
    }

    function () {
        throw; // this is a business contract, no donations
    }
}
