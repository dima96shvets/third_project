Project Overview and Requirements :
Every important part of this document will be assigned a reference number to streamline the testing process and improve
clarity within this document.

1. Project Scope and Overview :

    1.1 This is a web application designed to provide users with basic information about various games, along with the
    option to leave comments (3.2) on each game’s page, enhancing the user experience.

    1.2 The admin panel allows administrators to add, update, or delete games from the database and delete
    comments (2.3, 2.4).

2. Main Functionality and Page Logic :

    2.1 Homepage:
        The homepage displays clickable images of eight games preloaded into the database (3.1). Each image links to a
        dedicated game page with detailed game information (2.2).

    2.2 Game Page:
        On each game’s page, users can view the game’s name, developer, publisher, release date, and description.
        Guests (users without login) can leave a comment by entering their name and comment in the respective
        fields (3.2).
    All comments are saved and displayed below the game’s details on the game page.

    2.3 Login Page:
    The site includes an admin panel accessible only with the correct credentials entered on the login page. The admin
    must enter the correct "Username" and "Password." The current credentials for admin access are:
        - Username: admin
        - Password: password123

    2.4 Admin page:
    The admin panel grants permissions to: - Add (2.4.1) a new game to the database - Update (2.4.2) an existing game’s
    information - Delete (2.4.3) games from the database - Delete (2.4.4) user comments from the database.

             **Logic for Adding, Updating, and Deleting Games and Comments**:
        - 2.4.1:
            Adding a game requires filling in all fields except the **Game ID**, which the program will
            auto-generate. If no image is uploaded, a default image ("default.jpg") is assigned automatically.
        - 2.4.2:
            Updating a game requires entering the **Game ID** and at least one additional field (such as game
            name, description, developer, publisher, release date, or game image).
        - 2.4.3:
            Deleting a game requires only the **Game ID**. **Note:** Any associated comments should be deleted
            automatically when the game is removed(2.4.4).
        - 2.4.4:
            Deleting a comment requires entering the **Comment ID** in the designated field.

        - 2.4.5: Field Format and Length:
            - **Game Name**: max length 100 characters;
            - **Description**: max length 800 characters;
            - **Developer**: max length 100 characters;
            - **Publisher**: max length 100 characters;
            - **Release Date**: Date-picker component in `mm/dd/yyyy` format;
            - **Game Picture**: Upload in `.jpg` format only.

        - 2.4.6: Instructions Button:
            The admin page includes an **Instructions** button at the top, guiding users with the following message:
            "Leave the ID field empty when adding a new game. For updating or deleting, fill in the ID field and the
            fields you want to update (or just the ID for deletion). To delete a comment, select the comment ID from the
            list and click Submit."


    This functionality helps to manage the content on the site and keep game information up to date.

3. Database :

    3.1 The default database contains eight "main" games upon release, preloaded for testing: -
        1. 'Cyberpunk 2077', 2. 'Days Gone', 3. 'Dead Cells', 4. 'Death Stranding', 5. 'Deus Ex: Mankind Divided',
        6. 'Gothic II', 7. 'Prey (2017)', and 8. 'The Last of Us Part II'.

    3.2 Comment Section Logic:
        Users must fill out both the Name and Comment fields to post a comment. Maximum Lengths:
        Name: 80 characters. Comment: 800 characters.
        When all conditions are met, the comment will display on the game page, showing the Name, Posting Time,
        and the Comment text.

4. Testing directives :

    4.1 Only the Google Chrome web browser is currently within the testing scope.

    4.2 For testing purposes, use the following abbreviations to simplify the main functionalities:
        a: adding
        u: updating
        d: deleting
        g: game
        c: commenting
        ete: end-to-end
        p: page
        ap: admin page
        hp: homepage
        gp: game page
        lp: login page
        neg: negative
        pos: positive

