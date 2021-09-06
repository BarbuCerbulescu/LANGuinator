
##  LANGuinator <sub>  bot for Discord </sub>

### Summary:

<p>In essence, LANGuinator is a Discord bot that allows the encryption of messages in a certain ’language’, so that only those that ’know’ that particular language can decrypt it.</p>

<p>Each language has an associated cypher, which can be of three types: affine, Hill or Vigenere. </p>

<p>Languages only function within the server where they were created. It is possible, however, to import the cypher of a language from another server with approval from one of that server’s administrators.</p>

<p>LANGuinator possesses an experience-based system, where users become more ’fluent’ in a language the more messages they encrypt/decrypt in/from that particular language.</p> 

### How to create a language:
<p>If you administer a server with LANGuinator in it, all you need to do is use the <code>!lang create_language (language_name) (cypher_type)</code> command, where <code>(language_name)</code> is the name of the language you wish to create and <code>(cypher_type)</code> specifies the type of cypher the new language will have ( should be either 'affine', 'Hill' or 'Vigenere' ). The <code>cypher_type</code> parameter is optional and will be treated as 'affine' by default. A randomly-initialized cypher of the given type will be used for the newly created language ( see the notes below ). </p> 

<p>This command also creates a number of roles associated with that language equal to the number of levels of fluency. These roles will be used to determine how well a server member knows the language.</p>

 **Languages name are unique and serve as identifiers for the language within the server** 

### Encrypting/ decrypting messages
<p> To encrypt a message you can use the '<code>!lang encrypt (message) (language_name)</code>, where <code>(message)</code> is the message to be encrypted and <code>(language_name)</code> is the name of the language you wish to encrypt the message in. The bot will immediatly delete the message calling the <code>encrypt</code> command and post the encrypted message (along with the name of language) on the same channel </p>

### Levels of fluency
<p> There are three levels of fluency: begginer, intermediate and advanced. As of right now, these levels serve no real purpose but in the future they should affect the accuracy of message encryption/decryption for the given language.</p>
  
<p>When a user encrypts/decrypts a message in/from a language, he will gain a number of xp points equal to the length of the message. The ammount of xp points that the user has is used to determine his fluency for that language </p>

<p> A user can see the fluency level he has in each language, as well as the xp points necessary to level-up, by using the <code>!lang send_my_xp_status</code> command.</p>

### How to import a language:
<p>f you administer a server with LANGuinator in it, you can use the <code>!lang import_language (language_name) (guild_id)</code> command, where <code>(language_name)</code> is the name of the language you wish to import and <code>(guild_id)</code> is the name of the server you wish to import it from. In its current implementation, a language with the same name must be created before importing. Its cypher will then be overwritten if the import is approved.</p>
  
 <p>Upon using the command, a request will be sent to all non-bot adminstrators of the given server in the form of a private message. If one of the admins reacts with a <code>👍</code> emoji to the message, the request is considered approved and the language cypher will be imported. The admin may also deny the request by reacting with a <code>👎</code> to the same message. In either case, the bot will notify you of their decision.</p> 
  

### Notes on cypher initialization:
<p>The matrices used for the Hill cyphers will be either 2x2, 3x3 or 4x4.</p>

<p>The keys for the Vigenere cyphers will be composed of 5 to 10 random letters.</p>


