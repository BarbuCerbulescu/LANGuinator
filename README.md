
##  LANGuinator <sub>  bot for Discord </sub>

### Summary:

<p>In essence, LANGuinator is a Discord bot that allows the encryption of messages in a certain ’language’, so that only those that ’know’ that particular language can decrypt it.</p>

<p>Each language has an associated cypher, which can be of three types: affine, Hill or Vigenere. </p>

<p>Languages only function within the server where they were created. It is possible, however, to import the cypher of a language from another server with approval from one of that server’s administrators.</p>

<p>LANGuinator possesses an experience-based system, where users become more ’fluent’ in a language the more messages they encrypt/decrypt in/from that particular language.</p> 

### How to create a language:
<p>If you administer a server with LANGuinator in it, all you need to do is use the <code>!lang create_language (language_name) (cypher_type)</code> command, where <code>(language_name)</code> is the name of the language you wish to create and <code>(cypher_type)</code> specifies the type of cypher the new language will have ( should be either 'affine', 'Hill' or 'Vigenere' ). The <code>cypher_type</code> parameter is optional and will be treated as 'affine' by default. A randomly-initialized cypher of the given type will be used for the newly created language ( see the notes below ). </p> 
<p>This command also creates a number of roles associated with that language equal to the number of levels of fluency. These roles will be used to determine how well a server member knows the language.</p>

###



### Notes on cypher initialization:
<p>The matrices used for the Hill cyphers will be either 2x2, 3x3 or 4x4.</p>

<p>The keys for the Vigenere cyphers will be composed of 5 to 10 random letters.</p>


