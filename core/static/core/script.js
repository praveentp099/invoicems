document.addEventListener('DOMContentLoaded', function() {
    // Dropdown functionality
    const dropdowns = document.querySelectorAll('.sidebar .dropdown > a');
    
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Close other open dropdowns
            document.querySelectorAll('.dropdown').forEach(item => {
                if (item !== this.parentElement) {
                    item.classList.remove('active');
                }
            });
            
            // Toggle current dropdown
            this.parentElement.classList.toggle('active');
        });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        const isDropdown = e.target.closest('.dropdown');
        if (!isDropdown) {
            document.querySelectorAll('.dropdown').forEach(item => {
                item.classList.remove('active');
            });
        }
    });
    
    // Prevent dropdown menu clicks from closing the menu
    document.querySelectorAll('.dropdown-menu').forEach(menu => {
        menu.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    });
    
    // INVOICE FORM CALCULATIONS
    if (document.getElementById('invoice-form')) {
        // Calculate amounts in invoice form
        document.querySelectorAll('.item-row').forEach(row => {
            attachRowCalculations(row);
        });
        
        // Add new item row functionality
        const addItemButton = document.getElementById('add-item');
        if (addItemButton) {
            addItemButton.addEventListener('click', function() {
                const tableBody = document.getElementById('item-rows');
                const newRow = document.querySelector('.item-row').cloneNode(true);
                
                // Clear values
                const inputs = newRow.querySelectorAll('input');
                inputs.forEach(input => {
                    if (input.type !== 'hidden') {
                        input.value = '';
                    }
                });
                
                // Reset delete checkbox
                const deleteCheckbox = newRow.querySelector('input[type="checkbox"]');
                if (deleteCheckbox) {
                    deleteCheckbox.checked = false;
                }
                
                // Reset amount display
                newRow.querySelector('.amount').textContent = '0.00';
                
                // Add remove functionality
                const removeBtn = newRow.querySelector('.remove-row');
                removeBtn.addEventListener('click', function() {
                    newRow.remove();
                    calculateTotalAmount();
                });
                
                // Attach calculation events
                attachRowCalculations(newRow);
                
                // Add to table
                tableBody.appendChild(newRow);
                
                // Update form count
                const totalForms = document.getElementById('id_items-TOTAL_FORMS');
                totalForms.value = parseInt(totalForms.value) + 1;
            });
        }
        
        // Function to attach calculations to a row
        function attachRowCalculations(row) {
            const inputs = row.querySelectorAll('input[type="number"], input[type="text"]');
            inputs.forEach(input => {
                input.addEventListener('input', function() {
                    calculateRowAmount(row);
                    calculateTotalAmount();
                });
            });
            
            // Add remove row functionality
            const removeBtn = row.querySelector('.remove-row');
            if (removeBtn) {
                removeBtn.addEventListener('click', function() {
                    const deleteCheckbox = row.querySelector('input[type="checkbox"]');
                    if (deleteCheckbox) {
                        deleteCheckbox.checked = true;
                        row.style.display = 'none';
                    } else {
                        row.remove();
                    }
                    calculateTotalAmount();
                });
            }
        }
        
        // Calculate single row amount
        function calculateRowAmount(row) {
            const quantity = parseFloat(row.querySelector('[name$="-quantity"]').value) || 0;
            const unit_price = parseFloat(row.querySelector('[name$="-unit_price"]').value) || 0;
            const tax = parseFloat(row.querySelector('[name$="-tax"]').value) || 0;
            
            // Calculate amount
            let amount = quantity * unit_price;
            if (tax) {
                amount += amount * (tax / 100);
            }
            
            row.querySelector('.amount').textContent = amount.toFixed(2);
            return amount;
        }
        
        // Calculate total amount for all items
        function calculateTotalAmount() {
            let total = 0;
            document.querySelectorAll('.item-row').forEach(row => {
                if (row.style.display !== 'none') {
                    total += calculateRowAmount(row);
                }
            });
            document.getElementById('total-amount').textContent = total.toFixed(2);
        }
        
        // Initialize calculations
        calculateTotalAmount();
    }
    
    // QUOTE FORM CALCULATIONS
    if (document.getElementById('quote-form')) {
        // Calculate amounts in quote form
        document.querySelectorAll('.item-row').forEach(row => {
            attachQuoteRowCalculations(row);
        });
        
        // Add new item row functionality
        const addItemButton = document.getElementById('add-item');
        if (addItemButton) {
            addItemButton.addEventListener('click', function() {
                const tableBody = document.getElementById('item-rows');
                const newRow = document.querySelector('.item-row').cloneNode(true);
                
                // Clear values
                const inputs = newRow.querySelectorAll('input');
                inputs.forEach(input => {
                    if (input.type !== 'hidden') {
                        input.value = '';
                    }
                });
                
                // Reset delete checkbox
                const deleteCheckbox = newRow.querySelector('input[type="checkbox"]');
                if (deleteCheckbox) {
                    deleteCheckbox.checked = false;
                }
                
                // Reset amount display
                newRow.querySelector('.amount').textContent = '0.00';
                
                // Add remove functionality
                const removeBtn = newRow.querySelector('.remove-row');
                removeBtn.addEventListener('click', function() {
                    newRow.remove();
                    calculateQuoteTotalAmount();
                });
                
                // Attach calculation events
                attachQuoteRowCalculations(newRow);
                
                // Add to table
                tableBody.appendChild(newRow);
                
                // Update form count
                const totalForms = document.getElementById('id_items-TOTAL_FORMS');
                totalForms.value = parseInt(totalForms.value) + 1;
            });
        }
        
        // Function to attach calculations to a row
        function attachQuoteRowCalculations(row) {
            const inputs = row.querySelectorAll('input[type="number"], input[type="text"]');
            inputs.forEach(input => {
                input.addEventListener('input', function() {
                    calculateQuoteRowAmount(row);
                    calculateQuoteTotalAmount();
                });
            });
            
            // Add remove row functionality
            const removeBtn = row.querySelector('.remove-row');
            if (removeBtn) {
                removeBtn.addEventListener('click', function() {
                    const deleteCheckbox = row.querySelector('input[type="checkbox"]');
                    if (deleteCheckbox) {
                        deleteCheckbox.checked = true;
                        row.style.display = 'none';
                    } else {
                        row.remove();
                    }
                    calculateQuoteTotalAmount();
                });
            }
        }
        
        // Calculate single row amount
        function calculateQuoteRowAmount(row) {
            const quantity = parseFloat(row.querySelector('[name$="-quantity"]').value) || 0;
            const rate = parseFloat(row.querySelector('[name$="-rate"]').value) || 0;
            const discount = parseFloat(row.querySelector('[name$="-discount"]').value) || 0;
            const tax = parseFloat(row.querySelector('[name$="-tax"]').value) || 0;
            
            // Calculate amount
            let amount = quantity * rate;
            if (discount) {
                amount -= amount * (discount / 100);
            }
            if (tax) {
                amount += amount * (tax / 100);
            }
            
            row.querySelector('.amount').textContent = amount.toFixed(2);
            return amount;
        }
        
        // Calculate total amount for all items
        function calculateQuoteTotalAmount() {
            let total = 0;
            document.querySelectorAll('.item-row').forEach(row => {
                if (row.style.display !== 'none') {
                    total += calculateQuoteRowAmount(row);
                }
            });
            document.getElementById('total-amount').textContent = total.toFixed(2);
        }
        
        // Initialize calculations
        calculateQuoteTotalAmount();
    }
});