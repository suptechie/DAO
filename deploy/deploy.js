//first run code.js to import the compiled source code
//before you do that run compile.py to compile the latest version of the software in DAO/

var _defaultServiceProvider = web3.eth.accounts[0];
var daoContract = web3.eth.contract(dao_abi);
var min_value = 1;
var closing_time = 1459809456 + 3600

console.log("Creating DAOCreator Contract");
var creatorContract = web3.eth.contract(creator_abi);
var _daoCreatorContract = creatorContract.new(
    {
	from: web3.eth.accounts[0],
	data: creator_bin,
	gas: 2000000
    }, function (e, contract){
	if (e) {
            console.log(e+" at DAOCreator creation!");
	} else if (typeof contract.address != 'undefined') {
        var dao = daoContract.new(
	    _defaultServiceProvider,
	    contract.address,
	    web3.toWei(min_value, "ether"),
            0,
		    {
		        from: web3.eth.accounts[0],
		        data: dao_bin,
		        gas: 4000000
		    }, function (e, contract) {
		        // funny thing, without this geth hangs
		        console.log("At DAO creation callback");
		        if (typeof contract.address != 'undefined') {
 
		        }
		    });

	}
    });
