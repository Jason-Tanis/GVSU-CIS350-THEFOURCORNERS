Manual testing for Degree Dollars

## Test Case: Inputs Within Creating New Budget
**Objectives**: Verify that inputs work reasonably

**Steps**:
1. Open the Degree Dollars app in emulator
2. Click view my budget button
3. Click create new budget button
4. Enter input into subsection name field
5. Enter input into "0.00" input field
6. Press save budget and see what is shown in shell

**Expected Results**:
- Any name can be input for subsection
- Dollar amount should be reasonable amount, even if over billion but not negative

**Actual Results**:
- Subsection naming works, even if gibberish
- Subsection naming does allow numbers to be saved for the subsection name
- No text can be inputted for dollar amount
- Inputs for dollar amount have to delete the "0.00" first then put in amount
- If putting more cents within ".00", the input rounds to nearest cent
- Inputs for dollar amount can just over a billion at least
- However, there is certain limit for the dollar amount where the amount would go back to "0.0". Limit is unsure, 
- If dollar amount is negative, the dollar amouunt go back to "0.0"

## Test Case: Addings sections and subsections
**Objectives**: Verify if sections can be added

**Steps**:
1. Open the Degree Dollars app in emulator
2. Click view my budgets button
3. Click create new budget button
4. Add subsections with "ADD SUBSECTION" +" button
5. Add primary sections with "ADD SECTION +" button

**Expected Results**:
- New subsections are created under the previous subsections
- New subsections can input the text and numbers for their respective input fields
- New sections are created under the previous sections
- New sections can be renamed

**Actual Results**
- New subsection is created right under previous subsections
- New sections are created under the previous
- New subsections can input text and numbers to their respective input fields
- New sections can not be renamed

## Test Case: (WIP)




