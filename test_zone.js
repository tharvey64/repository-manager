// code
var fahrenheit_to_celsius = function(num){

};

var celsius_to_fahrenheit = function(num){
    return num;
};
var Jasmine = require('jasmine');

// NEW
var jasmineEnv = new Jasmine();
// NEW
// This is Stupid
var jasmine = jasmineEnv.jasmine;
// NEW
var custom_matchers = require('./jasmine-custom-matchers');
// tests


describe("Fahrenheit to Celsius", function(){
    beforeAll(function(){
        this.inputs = [32, 10, 75, 245];
        this.outputs = [0, -12.22, 23.89, 118.33];
    });

    beforeEach(function(){
        jasmine.addMatchers(custom_matchers({variable:'fahrenheit_to_celsius'}));
    });

    for(var idx = this.inputs.length;i--;){
        it(this.inputs[idx].toString(), function(){
            expect(fahrenheit_to_celsius).toBeDefined();
            expect(fahrenheit_to_celsius).toBeAFunction();
            expect(fahrenheit_to_celsius(this.inputs[idx])).toBeANumber();
            expect(fahrenheit_to_celsius(this.inputs[idx])).toBeCloseTo(this.outputs[idx], 2);
        });
    }

});

fdescribe("Celsius to Fahrenheit", function(){
    beforeAll(function(){
        this.inputs = [0, 10, 75, 245];
        this.outputs = [32, 50, 167, 473];
    });

    beforeEach(function(){
        jasmine.addMatchers(custom_matchers({variable:'celsius_to_fahrenheit'}));
    });

    for(var idx = this.inputs.length;i--;){
        it(this.inputs[idx].toString(), function(){
            expect(celsius_to_fahrenheit).toBeDefined();
            expect(celsius_to_fahrenheit).toBeAFunction();
            expect(celsius_to_fahrenheit(this.inputs[idx])).toBeANumber();
            expect(celsius_to_fahrenheit(this.inputs[idx])).toBeCloseTo(this.outputs[idx], 2);
        });
    }

});

// NEW
jasmineEnv.execute();