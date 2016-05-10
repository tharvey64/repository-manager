// Turn this into a function with options for each type of matcher
module.exports = function(options){
    return {
        toBeAFunction: function(util, customEqualityTesters){
            return {
                compare: function(actual){
                    var result = {};
                    result.pass = typeof actual === "function";
                    if (!result.pass){
                        result.message = "Expected " + options.variable + " to be a function"
                    }
                    return result;
                },
            };//end of return
        },
        toBeANumber: function(util, customEqualityTesters){
            console.log(arguments);
            return {
                compare: function(actual){
                    var result = {};
                    result.pass = typeof actual === "number";
                    if (!result.pass){
                        result.message = "Expected " + actual + " to be a number. Found " +typeof actual+ " instead."
                    }
                    return result;
                },
            };//end of return
        },
        toBeDefined: function(util, customEqualityTesters){
            return {
                compare: function(actual){
                    var result = {};
                    result.pass = void 0 !== actual;
                    if (!result.pass){
                        result.message = "Expected " + options.variable + " to be to define.";
                    }
                    return result;
                },
            };
        },
    };
};//end of module.exports