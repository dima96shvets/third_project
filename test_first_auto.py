import pytest
import time
from datetime import datetime
from conftest import base_url, randomstring, admin_login, date_generation
from app import Game, Comments
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains


@pytest.mark.usefixtures('driver', 'wait')
class TestUnit:

    @pytest.mark.positive
    @pytest.mark.unit
    def test_c_posting(self, driver, wait, assertion_handling, log_results):
        """
        preconditions: At least one game is available on the homepage to post a comment(3.1).
        (Verifies that a comment can be posted by a guest user, displaying a success message and listing the comment
         under the game’s comments section)
        references: 2.2, 3.2
        """
        sa, errors = assertion_handling

        test_name = "Test user"
        test_comment = "Test comment for unit testing"

        driver.find_element(By.XPATH, '(//div[@class="game-item"]/a)[1]').click()
        driver.find_element(By.XPATH, "//input[@id='name']").send_keys(test_name)
        driver.find_element(By.ID, 'comment').send_keys(test_comment)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        sa(driver.find_element(By.CLASS_NAME, "success").is_displayed(), "The success message did not appear")

        comments = driver.find_elements(By.CSS_SELECTOR, "ul li")
        found_comment = any(test_name in comment.text and test_comment in comment.text for comment in comments)
        sa(found_comment, "The comment doesn't appear in comment section")

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)

    @pytest.mark.unit
    def test_c_posting_time(self, driver, wait, assertion_handling, log_results):
        """
        preconditions: At least one game is available on the homepage to post a comment(3.1).
        (Verifies that a comment's posting time displays correctly and matches the current time in UTC format)
        references: 2.2, 3.2
        """
        sa, errors = assertion_handling

        test_name = "Test User for timestamp verification"
        test_comment = "Test comment for timestamp verification"
        current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M")

        driver.find_element(By.XPATH, '(//div[@class="game-item"]/a)[1]').click()
        driver.find_element(By.XPATH, "//input[@id='name']").send_keys(test_name)
        driver.find_element(By.ID, 'comment').send_keys(test_comment)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        sa(driver.find_element(By.CLASS_NAME, "success").is_displayed(), "The success message was not displayed")

        displayed_time = driver.find_element(By.XPATH,
                                             "(//div[@class='comments-section']//ul/li//span[@class='comment-time'])["
                                             "last()]").text
        displayed_time_clean = displayed_time.strip("() ")
        sa(current_time in displayed_time_clean,
           f"Displayed time '{displayed_time_clean}' does not contain the expected time - '{current_time}'")

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)


@pytest.mark.usefixtures('driver', 'wait')
class TestSanity:

    @pytest.mark.regression
    @pytest.mark.sanity
    def test_hp_sanity(self, driver, wait, assertion_handling, log_results):
        """
        preconditions: 8 games are in a database as expected(3.1).
        (Quick check that the homepage loads properly and has 8 games as expected)
        references: 2.1, 3.1
        """
        sa, errors = assertion_handling

        sa(driver.title == "Homepage - Game Selection", "Page title is incorrect.")
        sa(wait.until(EC.presence_of_element_located((By.XPATH, "//i[@class='fas fa-home']"))).is_displayed(),
           "Homepage button is not displayed")
        sa(wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".admin-button"))).is_displayed(),
           "Admin button is not displayed")
        game_items = driver.find_elements(By.CLASS_NAME, "game-item")
        sa(len(game_items) == 8, f"Expected 8 games displayed, found {len(game_items)}.")

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)


@pytest.mark.usefixtures('driver', 'wait')
class TestSmoke:
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_smoke_navigation(self, driver, wait, assertion_handling, log_results):
        """
        preconditions: 8 games are in a database as expected(3.1).
        (Quick validation of main site functionalities including navigation and key elements)
        references: 2.1, 2.2, 2.3, 2.4
        """
        sa, errors = assertion_handling

        # Homepage Navigation
        driver.get(base_url)
        sa(driver.title == "Homepage - Game Selection", "Homepage doesn't open or its title is incorrect")
        sa(wait.until(EC.presence_of_element_located((By.CLASS_NAME, "game-item"))).is_displayed(),
           "Game list is not displayed on the homepage")
        sa(wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".admin-button"))).is_displayed(),
           "Admin button is not visible on the homepage")
        game_items = driver.find_elements(By.CLASS_NAME, "game-item")
        sa(len(game_items) == 8, f"Expected 8 games displayed, found {len(game_items)}.")

        # Game Page Navigation
        driver.find_element(By.XPATH, '(//div[@class="game-item"]/a)[1]').click()
        sa(driver.current_url.startswith(f"{base_url}/game/"), "Failed to navigate to a game details page")
        sa(wait.until(EC.presence_of_element_located((By.CLASS_NAME, "game-info"))).is_displayed(),
           "Game information is not displayed on the game page")

        # Comment Section Check
        test_name = randomstring(min_length=10, max_length=15)
        test_comment = f"{randomstring()} - part of smoke test - testing comment posting feature"
        sa(wait.until(EC.presence_of_element_located((By.CLASS_NAME, "comments-section"))).is_displayed(),
           "Comments section is not visible on the game page")
        driver.find_element(By.ID, 'name').send_keys(test_name)
        driver.find_element(By.ID, 'comment').send_keys(test_comment)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        sa(wait.until(EC.presence_of_element_located((By.CLASS_NAME, "success"))).is_displayed(),
           "Comment submission success message not displayed")
        comments = driver.find_elements(By.CSS_SELECTOR, "ul li")
        found_comment = any(test_name in comment.text and test_comment in comment.text for comment in comments)
        sa(found_comment, "The comment doesn't appear in comment section")

        # Admin Panel Access
        driver.get(f"{base_url}/login")
        driver.find_element(By.ID, 'username').send_keys("admin")
        driver.find_element(By.ID, 'password').send_keys("password123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        sa(driver.current_url == f"{base_url}/admin", "Failed to access the admin panel")
        sa(wait.until(EC.presence_of_element_located((By.ID, 'action'))).is_displayed(),
           "Dropdown for selecting actions is not displayed on the admin panel.")

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)


@pytest.mark.usefixtures('driver', 'wait')
class TestNonFunctional:
    @pytest.mark.nonfunctional
    @pytest.mark.performance
    @pytest.mark.regression
    def test_p_loadtime(self, driver, wait, assertion_handling, log_results):
        """
        preconditions: Site routes (home, game page, login, admin) must be predefined and accessible.
        (check different site pages load time)
        references: 2.1, 2.2, 2.3, 2.4
        """
        sa, errors = assertion_handling

        # Homepage load time checking
        start_time = time.time()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "game-item")))
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "home-button")))
        homepage_loadtime = time.time() - start_time
        sa(homepage_loadtime < 3, f"Homepage took {homepage_loadtime:.2f} seconds to load")

        # Game page load time checking
        driver.find_element(By.XPATH, '(//div[@class="game-item"]/a)[1]').click()
        start_time = time.time()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "comments-section")))
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "game-container")))
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "add-comment")))
        gamepage_loadtime = time.time() - start_time
        sa(gamepage_loadtime < 3, f"Gamepage took {gamepage_loadtime:.2f} seconds to load")

        # Login page load time checking
        driver.get(f"{base_url}/login")
        start_time = time.time()
        wait.until(EC.presence_of_element_located((By.ID, 'username')))
        wait.until(EC.presence_of_element_located((By.ID, 'password')))
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "home-button")))
        loginpage_loadtime = time.time() - start_time
        sa(loginpage_loadtime < 3, f"Login page took {loginpage_loadtime:.2f} seconds to load")

        # Admin page load time checking
        admin_login(driver)
        start_time = time.time()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "home-button")))
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "container")))
        admin_panel_loadtime = time.time() - start_time
        sa(admin_panel_loadtime < 3, f"Admin panel page took {admin_panel_loadtime:.2f} seconds to load")

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)


@pytest.mark.usefixtures('driver', 'wait')
class TestSecurity:
    @pytest.mark.security
    @pytest.mark.regression
    def test_back_refresh(self, driver, wait, assertion_handling, log_results):
        """
        preconditions: Access to an admin panel.
        (Validate that refreshing or navigating back does not grant unauthorized access to the admin panel)
        references: 2.3, 2.4
        """
        sa, errors = assertion_handling

        admin_login(driver)
        driver.refresh()
        sa(driver.current_url != f"{base_url}/admin", "Still accessing admin panel even after refreshing the page")

        driver.get(base_url)
        admin_login(driver)
        driver.get(base_url)
        driver.back()
        sa(driver.current_url != f"{base_url}/admin", "Still accessing admin panel even after going back to the page")

        driver.get(base_url)
        admin_login(driver)
        driver.get(base_url)
        driver.get(f"{base_url}/admin")
        sa(driver.current_url != f"{base_url}/admin", "Still accessing admin panel even after leaving it previously")

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)

    @pytest.mark.security
    @pytest.mark.regression
    def test_login_form_logic(self, driver, wait, assertion_handling, log_results):
        """
        preconditions: Access to an admin panel.
        (Testing login form logic for various input scenarios)
        references: 2.3
        """
        sa, errors = assertion_handling

        driver.get(f"{base_url}/login")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        sa(driver.current_url != f"{base_url}/admin",
           "Accessing admin panel even after leaving the login and password fields empty")

        driver.get(f"{base_url}/login")
        driver.find_element(By.XPATH, "//input[@id='username']").send_keys("admin")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        sa(driver.current_url != f"{base_url}/admin",
           "Accessing admin panel even after leaving the password field empty")

        driver.get(f"{base_url}/login")
        driver.find_element(By.XPATH, "//input[@id='password']").send_keys("password123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        sa(driver.current_url != f"{base_url}/admin",
           "Accessing admin panel even after leaving the username field empty")

        driver.get(f"{base_url}/login")
        driver.find_element(By.XPATH, "//input[@id='username']").send_keys("wronglogin")
        driver.find_element(By.XPATH, "//input[@id='password']").send_keys("wrongpassword")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        sa(driver.find_element(By.CSS_SELECTOR, ".flash-message.error").is_displayed(), "Error message not displayed")
        sa(driver.current_url != f"{base_url}/admin",
           "Accessing admin panel even after entering wrong data to the login and password fields")

        driver.get(f"{base_url}/login")
        driver.find_element(By.XPATH, "//input[@id='username']").send_keys("admin")
        driver.find_element(By.XPATH, "//input[@id='password']").send_keys("wrongpassword")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        sa(driver.find_element(By.CSS_SELECTOR, ".flash-message.error").is_displayed(), "Error message not displayed")
        sa(driver.current_url != f"{base_url}/admin",
           "Accessing admin panel even after entering wrong data to the password field, but login entered correctly")

        driver.get(f"{base_url}/login")
        driver.find_element(By.XPATH, "//input[@id='username']").send_keys("wronglogin")
        driver.find_element(By.XPATH, "//input[@id='password']").send_keys("password123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        sa(driver.find_element(By.CSS_SELECTOR, ".flash-message.error").is_displayed(), "Error message not displayed")
        sa(driver.current_url != f"{base_url}/admin",
           "Accessing admin panel even after entering wrong data to the login field, but password entered correctly")

        admin_login(driver)
        sa(driver.current_url == f"{base_url}/admin",
           "Not accessing admin panel even after entering correct data to both fields")

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)


@pytest.mark.usefixtures('driver', 'wait')
class TestUI:
    @pytest.mark.ui
    def test_ui_hp(self, driver, wait, assertion_handling, log_results):
        """
        preconditions: no.
        (Testing the UI side of the homepage)
        references: 2.1, 3.1
        """
        sa, errors = assertion_handling

        # Ensure the homepage loads correctly
        driver.get(base_url)
        sa(driver.title == "Homepage - Game Selection", "Homepage title is incorrect")

        # Verifying game titles
        game_titles = ['Cyberpunk 2077', 'Days Gone', 'Dead Cells', 'Death Stranding', 'Deus Ex: Mankind Divided',
                       'Gothic II', 'Prey (2017)', 'The Last of Us Part II']
        for title in game_titles:
            sa(wait.until(EC.presence_of_element_located((By.XPATH, f"//h3[text()='{title}']"))).is_displayed(),
               f"Game title '{title}' is not displayed")

        # Verifying that games presented on the home page are clickable and visible
        game_items = driver.find_elements(By.CSS_SELECTOR, ".game-item a")
        game_count = len(game_items)
        for index in range(1, game_count + 1):
            game_link = wait.until(EC.element_to_be_clickable((By.XPATH, f'(//div[@class="game-item"]/a)[{index}]')))
            sa(game_link.is_displayed(), f"Game link {index} is not displayed")

        # Checking picture of each game presented on the home page
        game_items = driver.find_elements(By.CSS_SELECTOR, ".game-item a")
        thumbnails = driver.find_elements(By.CSS_SELECTOR, ".game-item img")
        sa(len(game_items) == len(thumbnails), "Mismatch between the number of game items and game thumbnails")
        for thumbnail in thumbnails:
            sa(thumbnail.is_displayed(), "One of the game thumbnails is not displayed")

        # Verifying that hover-effect of every thumbnail works correct
        action = ActionChains(driver)
        for thumbnail in thumbnails:
            action.move_to_element(thumbnail).perform()

        # "home page" button and "admin" button check
        sa(wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".home-button"))).is_displayed(),
           "Home page button is not displayed")
        sa(wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".admin-button"))).is_displayed(),
           "Admin button is not displayed")

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)

    @pytest.mark.ui
    def test_ui_gp(self, driver, wait, assertion_handling, log_results):
        """
        preconditions: no.
        (Checking the UI side of game page 1)
        references: 2.2, 3.2
        """
        sa, errors = assertion_handling

        driver.get(f"{base_url}/game/1")
        sa(driver.current_url == f"{base_url}/game/1", "Not accessing game page 1")

        # Ensure the homepage loads correctly
        game_name_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".game-info h1")))
        game_name = game_name_element.text
        sa(driver.title == game_name, f"Game page title is incorrect, expected: {game_name}")

        # Checking that the game image is displayed
        game_image = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".game-image")))
        sa(game_image.is_displayed(), "The game image is missing on the game page")

        # "home page" button check
        sa(wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".home-button"))).is_displayed(),
           "Home page button is not displayed")

        # checking the radio button feature (description)
        description_radio = driver.find_element(By.XPATH, "//input[@type='radio' and @value='description']")
        description_radio.click()
        sa(description_radio.is_selected(), "Description radio button is not selected after clicking")
        description_content = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".game-description")))
        sa(description_content.is_displayed(),
           "Description content is not displayed after selecting 'Description' radio button")

        # checking the radio button feature (game info)
        game_info_radio = driver.find_element(By.XPATH, "//input[@type='radio' and @value='info']")
        game_info_radio.click()
        sa(game_info_radio.is_selected(), "Game Info radio button is not selected after clicking")
        game_info_content = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".game-info-content")))
        sa(game_info_content.is_displayed(),
           "Game Info content is not displayed after selecting 'Game Info' radio button")

        # checking that the comment section exists
        comment_section = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".comments-section")))
        sa(comment_section.is_displayed(), "Comment section is not displayed on the page")

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)

    @pytest.mark.ui
    def test_ui_lp(self, driver, wait, assertion_handling, log_results):
        """
        preconditions: no.
        (Checking the UI side of login page)
        references: 2.3
        """
        sa, errors = assertion_handling

        driver.get(f"{base_url}/login")
        sa(driver.current_url == f"{base_url}/login", "Not accessing login page")

        # "home page" button check
        sa(wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".home-button"))).is_displayed(),
           "Home page button is not displayed")

        # Checking the login page title
        sa(driver.title == "Login Page", "Login page title is incorrect")

        # Checking the presence of input fields (Username and Password)
        username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
        password_field = wait.until(EC.presence_of_element_located((By.ID, "password")))
        sa(username_field.is_displayed(), "Username field is not displayed")
        sa(password_field.is_displayed(), "Password field is not displayed")

        # Checking that input fields are enabled for typing
        sa(username_field.is_enabled(), "Username field is not enabled for typing")
        sa(password_field.is_enabled(), "Password field is not enabled for typing")

        # Check the presence and functionality of the login button
        login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
        sa(login_button.is_displayed(), "Login button is not displayed")
        action = ActionChains(driver)
        action.move_to_element(login_button).perform()
        sa(login_button.is_enabled(), "Login button is not clickable when hovered")

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)

    @pytest.mark.ui
    def test_ui_ap(self, driver, wait, assertion_handling, log_results):
        """
        preconditions: no.
        (Checking the UI side of admin page)
        references: 2.4
        """
        sa, errors = assertion_handling

        admin_login(driver)
        sa(driver.current_url == f"{base_url}/admin",
           "Not accessing admin panel")

        # Checking the admin page title
        sa(driver.title == "Admin Page", "Admin page title is incorrect")

        # "home page" button check
        sa(wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".home-button"))).is_displayed(),
           "Home page button is not displayed")

        # Verifying the presence and visibility of input fields (Game ID, Comment ID, Game Name, Description,
        # Developer, Publisher, Release Date)
        game_id_field = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Game ID']")))
        comment_id_field = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Comment ID']")))
        game_name_field = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Game Name']")))
        description_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder='Game "
                                                                                        "Description']")))
        developer_field = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Developer']")))
        publisher_field = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Publisher']")))
        releasedate_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='releasedate']")))

        sa(game_id_field.is_displayed(), "Game ID field is not displayed")
        sa(comment_id_field.is_displayed(), "Comment ID field is not displayed")
        sa(game_name_field.is_displayed(), "Game name field is not displayed")
        sa(description_field.is_displayed(), "Game description field is not displayed")
        sa(developer_field.is_displayed(), "Developer field is not displayed")
        sa(publisher_field.is_displayed(), "Publisher field is not displayed")
        sa(releasedate_field.is_displayed(), "Releasedate field is not displayed")

        # Checking that input fields are enabled for input
        sa(game_id_field.is_enabled(), "Game ID field is not enabled for input")
        sa(comment_id_field.is_enabled(), "Comment ID field is not enabled for input")
        sa(game_name_field.is_enabled(), "Game name field is not enabled for input")
        sa(description_field.is_enabled(), "Game description field is not enabled for input")
        sa(developer_field.is_enabled(), "Game developer field is not enabled for input")
        sa(publisher_field.is_enabled(), "Game publisher field is not enabled for input")
        sa(releasedate_field.is_enabled(), "Release date field is not enabled for input")

        # Placeholder verification for guidance
        sa(game_id_field.get_attribute("placeholder") == "Game ID",
           "Game ID field placeholder is incorrect or missing")
        sa(comment_id_field.get_attribute("placeholder") == "Comment ID",
           "Comment ID field placeholder is incorrect or missing")
        sa(game_name_field.get_attribute("placeholder") == "Game Name",
           "Game Name field placeholder is incorrect or missing")
        sa(description_field.get_attribute("placeholder") == "Game Description",
           "Game Description field placeholder is incorrect or missing")
        sa(developer_field.get_attribute("placeholder") == "Developer",
           "Developer field placeholder is incorrect or missing")
        sa(publisher_field.get_attribute("placeholder") == "Publisher",
           "Publisher field placeholder is incorrect or missing")

        # checking hide/show "instructions" button
        instructions = driver.find_element(By.ID, "instructions-content")
        sa(not instructions.is_displayed(), "Instructions are visible by default but should be hidden")
        driver.find_element(By.CSS_SELECTOR, ".toggle-button").click()
        wait.until(EC.visibility_of(instructions))
        sa(instructions.is_displayed(), "Instructions should be displayed after clicking the button")
        driver.find_element(By.CSS_SELECTOR, ".toggle-button").click()
        wait.until_not(EC.visibility_of(instructions))
        sa(not instructions.is_displayed(), "Instructions should be hidden after clicking the button again")

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)


@pytest.mark.usefixtures('driver', 'wait', 'existence_checking')
class TestNegative:

    @pytest.mark.negative
    def test_c_posting_neg_empty_fields(self, driver, wait, assertion_handling, log_results):
        """
        preconditions: Comment form should not accept submissions with empty name or comment fields.
        (Attempting to post a comment with either the name or comment field left empty)
        references: 3.2
        """
        sa, errors = assertion_handling

        # Generating unique test values for name and comment fields
        test_name = randomstring(min_length=10, max_length=15)
        test_comment = randomstring(min_length=50, max_length=60)

        # Attempt to post a comment with the "comment" field left empty
        driver.find_element(By.XPATH, '(//div[@class="game-item"]/a)[1]').click()
        driver.find_element(By.XPATH, "//input[@id='name']").send_keys(test_name)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        success_message_elements = driver.find_elements(By.CLASS_NAME, "success")
        sa(len(success_message_elements) == 0,
           "Success message appeared despite the comment field being left empty")
        comments = driver.find_elements(By.CSS_SELECTOR, "ul li")
        found_name_comment = any(test_name in comment.text for comment in comments)
        sa(not found_name_comment, "A comment with the test name was added despite the comment field being left empty")

        driver.find_element(By.ID, 'name').clear()

        # Attempt to post a comment with the "name" field left empty
        driver.find_element(By.ID, 'comment').send_keys(test_comment)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        success_message_elements = driver.find_elements(By.CLASS_NAME, "success")
        sa(len(success_message_elements) == 0,
           "Success message appeared despite the name field being left empty")
        comments = driver.find_elements(By.CSS_SELECTOR, "ul li")
        found_comment = any(test_comment in comment.text for comment in comments)
        sa(not found_comment, "A comment with the test name was added despite the name field being left empty")

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)

    @pytest.mark.negative
    def test_c_posting_neg_invalid_values(self, driver, wait, assertion_handling, log_results):
        """
        preconditions: Comment form should restrict inputs exceeding the max field length.
        (Attempting to post comment with higher field length limits)
        references: 3.2
        """
        sa, errors = assertion_handling

        driver.find_element(By.XPATH, '(//div[@class="game-item"]/a)[1]').click()

        # Exceeding name field length (81 characters for name, 800 for comment)
        driver.find_element(By.ID, 'name').clear()
        driver.find_element(By.ID, 'comment').clear()

        driver.find_element(By.ID, 'name').send_keys(randomstring(length=81))
        driver.find_element(By.ID, 'comment').send_keys(randomstring(length=800))
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        sa(not driver.find_element(By.CLASS_NAME, "success").is_displayed(),
           "The success message was displayed even though the name field exceeded the allowed length")
        sa(not driver.find_elements(By.CSS_SELECTOR, "ul li"),
           "A comment appeared on the page despite exceeding the allowed name field length")

        # Exceeding name field length (80 for name, 801 for comment)
        driver.find_element(By.ID, 'name').clear()
        driver.find_element(By.ID, 'comment').clear()

        driver.find_element(By.ID, 'name').send_keys(randomstring(length=80))
        driver.find_element(By.ID, 'comment').send_keys(randomstring(length=801))
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        sa(not driver.find_element(By.CLASS_NAME, "success").is_displayed(),
           "The success message was displayed even though the comment field exceeded the allowed length")
        sa(not driver.find_elements(By.CSS_SELECTOR, "ul li"),
           "A comment appeared on the page despite exceeding the allowed comment field length")

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)

    @pytest.mark.negative
    def test_d_c_neg(self, driver, wait, assertion_handling, log_results):
        """
        preconditions: Admin panel should properly display error messages for invalid or empty field submissions.
        (Testing deleting comment function under negative scenarios)
        references: 2.4.4
        """
        sa, errors = assertion_handling

        admin_login(driver)
        sa(driver.current_url == f"{base_url}/admin",
           "Not accessing admin panel")

        # Attempting to delete a comment without any fields filled
        driver.find_element(By.XPATH, "//option[text()='Delete Comment']").click()
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        sa(driver.find_element(By.CSS_SELECTOR, ".error").is_displayed(), "Error message not shown when deleting "
                                                                          "comment with all fields empty")

        # Filling "Comment ID" with "Add Game" option selected, which should trigger an error
        driver.find_element(By.XPATH, "//option[text()='Add Game']").click()
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Comment ID']").send_keys("1")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        sa(driver.find_element(By.CSS_SELECTOR, ".error").is_displayed(), "Error message not shown when 'Comment ID' "
                                                                          "is filled with 'Add Game' option selected")

        # Filling other fields except "Comment ID" under "Delete Comment" option, which should trigger an error
        driver.find_element(By.XPATH, "//option[text()='Delete Comment']").click()
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Game Name']").send_keys(randomstring())
        driver.find_element(By.CSS_SELECTOR, "textarea[placeholder='Game Description']").send_keys(randomstring())
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Developer']").send_keys(randomstring())
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Publisher']").send_keys(randomstring())
        driver.find_element(By.CSS_SELECTOR, "input[name='releasedate']").send_keys(date_generation())
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        sa(driver.find_element(By.CSS_SELECTOR, ".error"), "Error message not shown when 'Delete Comment' option is "
                                                           "selected with non-comment fields filled")

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)

    @pytest.mark.negative
    def test_a_g_neg(self, driver, wait, assertion_handling, existence_checking, log_results):
        """
        preconditions: Access to an admin panel.
        (Attempting to add a game while leaving mandatory fields empty or exceeding field length limits)
        references: 2.4.5
        """
        sa, errors = assertion_handling

        admin_login(driver)
        sa(driver.current_url == f"{base_url}/admin",
           "Not accessing admin panel")

        new_game = randomstring()

        # Attempting to add a game without a description (required field test)
        driver.find_element(By.XPATH, "//option[text()='Add Game']").click()
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Game Name']").send_keys(new_game)
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Developer']").send_keys(randomstring())
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Publisher']").send_keys(randomstring())
        driver.find_element(By.CSS_SELECTOR, "input[name='releasedate']").send_keys(date_generation())
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        sa(len(driver.find_elements(By.CLASS_NAME, "success")) == 0,
           "Game was added despite missing required description field")
        sa(not existence_checking(Game, gamename=new_game), "Game was added to the database despite the missing "
                                                            "description")

        fields = [
            driver.find_element(By.CSS_SELECTOR, "input[placeholder='Game Name']"),
            driver.find_element(By.CSS_SELECTOR, "textarea[placeholder='Game Description']"),
            driver.find_element(By.CSS_SELECTOR, "input[placeholder='Developer']"),
            driver.find_element(By.CSS_SELECTOR, "input[placeholder='Publisher']")
        ]
        for field in fields:
            field.clear()

        # Attempting to add a game with overflow values in name and description fields
        long_game_name = randomstring(length=101)
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Game Name']").send_keys(long_game_name)
        driver.find_element(By.CSS_SELECTOR, "textarea[placeholder='Game Description']").send_keys(
            randomstring(length=801))
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Developer']").send_keys(randomstring())
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Publisher']").send_keys(randomstring())
        driver.find_element(By.CSS_SELECTOR, "input[name='releasedate']").send_keys(date_generation())
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        sa(len(driver.find_elements(By.CLASS_NAME, "success")) == 0, "Game was added despite field length exceeding "
                                                                     "limits")
        sa(not existence_checking(Game, gamename=long_game_name), "Game was incorrectly added to the database with "
                                                                  "overflow values")

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)


@pytest.mark.usefixtures('driver', 'wait', 'existence_checking')
class TestIntegration:
    @pytest.mark.regression
    @pytest.mark.integration
    def test_routes_checking(self, driver, wait, assertion_handling, log_results):
        """
        preconditions: Site routes (home, game page, login, admin) must be predefined and accessible.
        (Verifying that all main routes are accessible and show the correct content)
        references: 2.1, 2.2, 2.3, 2.4
        """
        sa, errors = assertion_handling

        # home page
        driver.get(f"{base_url}/")
        sa(driver.current_url == f"{base_url}/", "Homepage failed to open or URL is incorrect")
        sa(driver.title == "Homepage - Game Selection", "Homepage title is incorrect")
        sa(wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".home-button"))).is_displayed(),
           "Homepage button is missing")

        # game page 1
        driver.get(f"{base_url}/game/1")
        sa(driver.current_url == f"{base_url}/game/1", "Game page 1 failed to open or URL is incorrect")
        game_name_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".game-info h1")))
        game_name = game_name_element.text
        sa(driver.title == game_name, f"Game page title is incorrect, expected: {game_name}")

        # login page
        driver.get(f"{base_url}/login")
        sa(driver.current_url == f"{base_url}/login", "Login page failed to open or URL is incorrect")
        sa(driver.title == "Login Page", "Login page title is incorrect")
        sa(wait.until(EC.presence_of_element_located((By.ID, "username"))).is_displayed(),
           "Username field is missing on login page")
        sa(wait.until(EC.presence_of_element_located((By.ID, "password"))).is_displayed(),
           "Username field is missing on login page")

        # admin page
        admin_login(driver)
        sa(driver.current_url == f"{base_url}/admin", "Admin page failed to open or URL is incorrect after login")
        sa(driver.title == "Admin Page", "Admin page title is incorrect")

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)

    @pytest.mark.integration
    def test_a_g_a_c_d_g(self, driver, wait, assertion_handling, log_results, existence_checking):
        """
        preconditions: Access to an admin panel.
        (Adding a new game to the database, comment on it, and then delete the game to verify that
        associated comments are also removed)
        references: 2.4.1, 2.4.3, 3.2
        """
        sa, errors = assertion_handling

        admin_login(driver)
        sa(driver.current_url == f"{base_url}/admin",
           "Not accessing admin panel")

        # Adding game
        new_game = f"TestGame_{randomstring(5)}"
        driver.find_element(By.XPATH, "//option[text()='Add Game']").click()
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Game Name']").send_keys(new_game)
        driver.find_element(By.CSS_SELECTOR, "textarea[placeholder='Game Description']").send_keys("integration test")
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Developer']").send_keys(randomstring())
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Publisher']").send_keys(randomstring())
        driver.find_element(By.CSS_SELECTOR, "input[name='releasedate']").send_keys(date_generation())
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        sa(driver.find_element(By.CLASS_NAME, "success").is_displayed(), "Game addition success message missing")
        sa(existence_checking(Game, gamename=new_game), "Game was not added to database")

        game_element = driver.find_element(By.XPATH, f"//h4[contains(text(),'{new_game}')]")
        game_id_text = game_element.text
        game_id = game_id_text.split("ID: ")[1].replace(")", "").strip()
        game_element.click()

        # Commenting game
        test_name = f"User_{randomstring(5)}"
        test_comment = f"{randomstring()} - Integration test comment"

        driver.find_element(By.XPATH, "//input[@id='name']").send_keys(test_name)
        driver.find_element(By.ID, 'comment').send_keys(test_comment)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        sa(driver.find_element(By.CLASS_NAME, "success").is_displayed(), "Comment posting success message missing")

        comments = driver.find_elements(By.CSS_SELECTOR, "ul li")
        found_comment = any(test_name in comment.text and test_comment in comment.text for comment in comments)
        sa(found_comment, "The comment is missing in the comment section")

        admin_login(driver)
        sa(driver.current_url == f"{base_url}/admin",
           "Not accessing admin panel")

        # Deleting game
        driver.find_element(By.XPATH, "//select/option[text()='Delete Game']").click()
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Game ID']").send_keys(game_id)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        sa(driver.find_element(By.CLASS_NAME, "success").is_displayed(), "Game deletion success message missing")
        sa(not existence_checking(Game, gamename=new_game), "Game still exists in the database after deletion")
        sa(not existence_checking(Comments, commentatorsname=test_name, comment=test_comment),"Associated comment "
                                                                                              "still exists after "
                                                                                              "deleting the game")

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)

    @pytest.mark.acceptance
    @pytest.mark.ete
    @pytest.mark.regression
    @pytest.mark.integration
    def test_acceptance(self, driver, wait, assertion_handling, log_results, existence_checking):
        """
        preconditions: Access to an admin panel.
        (Verifying that main site functionality meets customer requirements and basic features work correctly)
        references: 2.4, 2.2, 3.2
        """
        sa, errors = assertion_handling

        admin_login(driver)
        sa(driver.current_url == f"{base_url}/admin",
           "Not accessing admin panel")

        new_game = randomstring()
        driver.find_element(By.XPATH, "//select/option[text()='Add Game']").click()
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Game Name']").send_keys(new_game)
        driver.find_element(By.CSS_SELECTOR, "textarea[placeholder='Game Description']").send_keys(randomstring())
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Developer']").send_keys(randomstring())
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Publisher']").send_keys(randomstring())
        driver.find_element(By.CSS_SELECTOR, "input[name='releasedate']").send_keys(date_generation())
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        sa(driver.find_element(By.CLASS_NAME, "success").is_displayed(), "The game was not added successfully")
        sa(existence_checking(Game, gamename=new_game), "Game not found in database after addition")

        driver.get(f"{base_url}/game/1")
        test_name = "Acceptance Test User"
        test_comment = "Acceptance test comment"
        driver.find_element(By.XPATH, "//input[@id='name']").send_keys(test_name)
        driver.find_element(By.ID, 'comment').send_keys(test_comment)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        sa(driver.find_element(By.CLASS_NAME, "success").is_displayed(), "Comment was not posted")

        comments = driver.find_elements(By.CSS_SELECTOR, "ul li")
        found_comment = any(test_name in comment.text and test_comment in comment.text for comment in comments)
        sa(found_comment, "The comment does not appear in the comment section after posting")

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)


@pytest.mark.usefixtures('driver', 'wait', 'existence_checking')
class TestFunctional:

    @pytest.mark.positive
    @pytest.mark.functional
    def test_aud_g(self, driver, wait, assertion_handling, existence_checking, log_results):
        """
        preconditions: Access to an admin panel.
        (Verifying adding, updating, and deleting a game in the admin panel)
        references: 2.4.1, 2.4.2, 2.4.3, 2.4.5
        """
        sa, errors = assertion_handling

        admin_login(driver)
        sa(driver.current_url == f"{base_url}/admin",
           "Not accessing admin panel")

        # Adding game
        new_game = randomstring()
        driver.find_element(By.XPATH, "//option[text()='Add Game']").click()
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Game Name']").send_keys(new_game)
        driver.find_element(By.CSS_SELECTOR, "textarea[placeholder='Game Description']").send_keys(randomstring())
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Developer']").send_keys(randomstring())
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Publisher']").send_keys(randomstring())
        driver.find_element(By.CSS_SELECTOR, "input[name='releasedate']").send_keys(date_generation())
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        sa(driver.find_element(By.CLASS_NAME, "success").is_displayed(), "Game addition success message not displayed")
        sa(existence_checking(Game, gamename=new_game), "Game was not added to database")

        game_element = driver.find_element(By.XPATH, f"//h4[contains(text(),'{new_game}')]")
        game_id_text = game_element.text
        game_id = game_id_text.split("ID: ")[1].replace(")", "").strip()

        # Updating game
        driver.find_element(By.XPATH, "//option[text()='Update Game']").click()
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Game ID']").send_keys(game_id)
        updated_description = "Updated Description :" + randomstring()
        driver.find_element(By.CSS_SELECTOR, "textarea[placeholder='Game Description']").send_keys(updated_description)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        sa(driver.find_element(By.CLASS_NAME, "success").is_displayed(), "Game update success message not displayed")
        sa(existence_checking(Game, gamename=new_game, description=updated_description),
           "Game was not updated in the database")

        # Deleting game
        driver.find_element(By.XPATH, "//select/option[text()='Delete Game']").click()
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Game ID']").send_keys(game_id)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        sa(driver.find_element(By.CLASS_NAME, "success").is_displayed(), "Game deletion success message not displayed")
        sa(not existence_checking(Game, gamename=new_game), "Game was not deleted from the database")

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)

    @pytest.mark.positive
    @pytest.mark.functional
    def test_d_c(self, driver, wait, assertion_handling, existence_checking, log_results):
        """
        preconditions: 1. At least one comment should exist in the database. 2. Access to an admin panel.
        (Deleting all existing comments from the admin panel)
        references: 2.4.6
        """
        sa, errors = assertion_handling

        admin_login(driver)
        sa(driver.current_url == f"{base_url}/admin",
           "Not accessing admin panel")

        comments_list = driver.find_elements(By.CSS_SELECTOR, "ul li")
        if not comments_list:
            log_results("passed", ["No comments found, nothing to delete."])
            return

        if comments_list:
            while driver.find_elements(By.CSS_SELECTOR, "ul li"):
                comment_element = driver.find_element(By.CSS_SELECTOR, "ul li")
                comment_text = comment_element.text
                comment_id = comment_text.split(":")[0].strip()

                driver.find_element(By.XPATH, "//select/option[text()='Delete Comment']").click()
                driver.find_element(By.CSS_SELECTOR, "input[placeholder='Comment ID']").send_keys(comment_id)
                driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
                sa(wait.until(EC.presence_of_element_located((By.CLASS_NAME, "success"))).is_displayed(),
                   f"Failed to delete comment with ID: {comment_id}")

                driver.refresh()
        sa(not driver.find_elements(By.CSS_SELECTOR, "ul li"), "Comments still exist after attempting to delete all")

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)
