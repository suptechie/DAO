//first run code.js to import the compiled source code
//before you do that run compile.py to compile the latest version of the software in DAO

personal.unlockAccount(eth.accounts[0]);
var _defaultServiceProvider = web3.eth.accounts[0];
var daoContract = web3.eth.contract(dao_abi);
var min_value = 1;
var closing_time = new Date().getTime() + seconds_from_now;

var creatorContract = web3.eth.contract(creator_abi);
console.log("Creating DAOCreator Contract");
var _daoCreatorContract = creatorContract.new(
    {
	    from: web3.eth.accounts[0],
	    data: dao_bin,
	    gas: 4000000
    }, function (e, contract){
	    if (e) {
            console.log(e+ " at DAOCreator creation!");
	    } else if (typeof contract.address != 'undefined') {
            console.log("Reached actual DAO creation");
            var dao = daoContract.new(
	            _defaultServiceProvider,
	            contract.address,
	            web3.toWei(min_value, "ether"),
                closing_time,
                0,
		        {
		            from: web3.eth.accounts[0],
		            data: dao_bin,
		            gas: 4000000
		        }, function (e, our_contract) {
		            // funny thing, without this geth hangs
		            console.log("At DAO creation callback");
		            if (typeof our_contract.address != 'undefined') {
                        console.log("our new DAO address is: " + our_contract.address);
		            }
		        });

	    }
    });
