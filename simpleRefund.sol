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

// TODO: all constants need to be double checked
import "github.com/slockit/DAO/DAO.sol";

contract Refund {
    DAO constant public mainDAO = DAO(0xbb9bc244d798123fde783fcc1c72d3bb8c189413);
    uint constant public totalSupply = 11712722930974665882186911;
    uint constant public totalWeiSupply = 12072858342395652843028271;

function withdraw(address donateExtraBalanceTo){
        uint balance = mainDAO.balanceOf(msg.sender);

        if (!mainDAO.transferFrom(this, balance)
            || !msg.sender.send(balance)
            || !donateExtraBalanceTo.send(balance * totalWeiSupply / totalSupply - balance)
           ) throw;
    }
}
