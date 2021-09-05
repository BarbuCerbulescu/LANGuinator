
##  LANGuinator <sub>  bot for Discord </sub>


### Summary:

<p>In essence, LANGuinator is a Discord bot that allows the encryption of messages in a certain ’language’, so that only those that ’know’ that particular language can decrypt it.</p>

<p>Each language has an associated cypher, which can be of three types: affine, Hill or Vigenere. </p>

<p>Languages only function within the server where they were created. It is possible , however, to import the cypher of a language from another server with approval from one of that server’s administrators.</p>

<p>LANGuinator possesses an experience-based system, where users become more ’fluent’ in a language the more messages they encrypt/decrypt in/from that particular language.</p> 

### How to create a language:
If you have LANGuinator as a member in your server, all you need to do is use the ```!lang create_language (language_name) (cypher_type)``` command, where (language_name) is the name of the language you wish to create and (cypher_type) specifies the type of cypher the new language will have ( should be either 'affine', 'Hill' or 'Vigenere' ). In addition, this command creates a number of roles equal to the number of levels of fluency.


