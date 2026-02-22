(function () {
  'use strict';

  angular
    .module('claimsApp', [])
    .controller('ClaimsController', ClaimsController);

  function ClaimsController() {
    var vm = this;

    vm.claimTypes = ['Vehicle', 'Health', 'Property', 'Travel', 'Life'];
    vm.claims = [
      {
        id: 1,
        policyNumber: 'POL-10021',
        type: 'Vehicle',
        amount: 1800,
        description: 'Rear bumper damage from parking lot accident.',
        status: 'Under Review',
        createdAt: new Date()
      }
    ];

    vm.newClaim = {
      policyNumber: '',
      type: '',
      amount: null,
      description: ''
    };

    vm.addClaim = function addClaim() {
      if (!vm.newClaim.policyNumber || !vm.newClaim.type || !vm.newClaim.amount) {
        return;
      }

      vm.claims.unshift({
        id: Date.now(),
        policyNumber: vm.newClaim.policyNumber,
        type: vm.newClaim.type,
        amount: Number(vm.newClaim.amount),
        description: vm.newClaim.description,
        status: 'Submitted',
        createdAt: new Date()
      });

      vm.newClaim = {
        policyNumber: '',
        type: '',
        amount: null,
        description: ''
      };
    };
  }
})();
