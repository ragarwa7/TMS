# TMS
Implementation of Truth Maintenance System (TMS)  in Python

The input of the TMS is a text file containing a sequence of actions that forces the TMS to add and retract multiple items. The system prints out the state of the knowledge base after each update. It should also recognize when a conflict has been created and alert the user.

In the input file, "*" means logical and (^), "+" represents logical or (V), "-" indicates logical negation (-), and ">" represents implication (->). All propositions are represented by single letter variables (e.g. "A"). Statements is grouped by parentheses.

For example, given the following input file:

        Tell:A>B
        Tell:A
        Tell:(A+-C)>D
        Tell:-C
        Retract:A
        Tell:C
        
The status of TMS after executing each step would be as follows:        
