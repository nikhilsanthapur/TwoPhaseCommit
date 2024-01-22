# TwoPhaseCommit



1.	The file that we have created are one coordinator and 3 participants Coordinator.py, Participant1.py, Participant2.py and Participant3.py.
2.	We run all the Programs in order to check the connection, voting everything are happening between the files.
3.	According to the First question in TC failure we run all the programs we use ctrl+shift+Pause/Break after the coordinator sends the message as ready for polling and as the reply, we get from all the 3 participants as Fail and abort.
4.	Second question in Node failure we run all the programs we use same above keys then the participant 3 without sending the ready then in the transaction it gets abort.
5.	Third question TC failure when the participant3 already ready for the polling but the transaction was stopped then when its reconnected it will get the commit after reconnecting to the transaction.
6.	Fourth question Node Failure when the Transaction with new file CoordinatorNew1.py was created and then the participants were get connected when the connection was started participant3 was reconnected then the reply in coordinator will be shown as commit.

