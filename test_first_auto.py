import pytest
import time
import emoji
from conftest import base_url, randomstring, admin_login, date_generation
from app import Game, Comments
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


@pytest.mark.usefixtures('driver', 'wait')
class TestUnit:

    @pytest.mark.positive
    @pytest.mark.regression
    def test_one(self, driver, wait, assertion_handling, log_results):
        """
        Unit testing ( basic logic of comment posting works and returns success message )
        """
        sa, errors = assertion_handling

        driver.find_element(By.XPATH, '(//div[@class="game-item"]/a)[1]').click()
        driver.find_element(By.XPATH, "//input[@id='name']").send_keys(randomstring())
        driver.find_element(By.ID, 'comment').send_keys("autotest number one")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        sa(driver.find_element(By.CLASS_NAME, "success").is_displayed(), "The success message was not displayed")

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)

    @pytest.mark.regression
    @pytest.mark.security
    def test_two(self, driver, wait, assertion_handling, log_results):
        """
        Unit testing ( testing the logic of login form )
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
           "Accessing admin panel even after leaving the login field empty")

        driver.get(f"{base_url}/login")
        driver.find_element(By.XPATH, "//input[@id='username']").send_keys("wronglogin")
        driver.find_element(By.XPATH, "//input[@id='password']").send_keys("wrongpassword")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
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
class TestSanity:
    @pytest.mark.sanity
    def test_three(self, driver, wait, assertion_handling, log_results):
        """
        Sanity testing ( quick checking that the homepage loads properly and as expected )
        """
        sa, errors = assertion_handling

        sa(driver.title == "Homepage - Game Selection", "Page title is incorrect.")
        sa(wait.until(EC.presence_of_element_located((By.XPATH, "//i[@class='fas fa-home']"))).is_displayed(),
           "Homepage button is not displayed.")
        sa(wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".admin-button"))).is_displayed(),
           "Admin button is not displayed.")
        sa(wait.until(EC.presence_of_element_located((By.CLASS_NAME, "game-item"))), "Game list is not displayed.")

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)


@pytest.mark.usefixtures('driver', 'wait')
class TestPerformance:
    @pytest.mark.regression
    @pytest.mark.performance
    def test_four(self, driver, wait, assertion_handling, log_results):
        """
        Performance testing ( checking the load time of different pages of the site )
        """
        sa, errors = assertion_handling

        start_time = time.time()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "game-item")))
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "home-button")))
        homepage_loadtime = time.time() - start_time
        sa(homepage_loadtime < 3, f"Homepage took {homepage_loadtime:.2f} seconds to load")

        driver.find_element(By.XPATH, '(//div[@class="game-item"]/a)[1]').click()
        start_time = time.time()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "comments-section")))
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "game-container")))
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "add-comment")))
        gamepage_loadtime = time.time() - start_time
        sa(gamepage_loadtime < 3, f"Gamepage took {gamepage_loadtime:.2f} seconds to load")

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
    @pytest.mark.regression
    @pytest.mark.security
    def test_five(self, driver, wait, assertion_handling, log_results):
        """
        Security testing ( trying to access admin panel by pressing "refresh" button and "back" button )
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

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)


@pytest.mark.usefixtures('driver', 'wait', 'existence_checking')
class TestFunctional:
    @pytest.mark.positive
    @pytest.mark.regression
    def test_six(self, driver, wait, assertion_handling, existence_checking, log_results):
        """
        Functional testing ( adding new game )
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
        sa(driver.find_element(By.CLASS_NAME, "success").is_displayed(), "Something went wrong, the game didn't added")
        sa(existence_checking(Game, gamename=new_game), "Game was not added to database")

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)


@pytest.mark.usefixtures('driver', 'wait')
class TestPlace:
    @pytest.mark.integration
    @pytest.mark.regression
    def test_seven(self, driver, wait, assertion_handling, log_results):
        """
        Functional testing ( updating game )
        """
        sa, errors = assertion_handling

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)


@pytest.mark.usefixtures('driver', 'wait')
class TestPlace:
    @pytest.mark.integration
    @pytest.mark.regression
    def test_eight(self, driver, wait, assertion_handling, log_results):
        """
        Functional testing ( deleting game )
        """
        sa, errors = assertion_handling

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)


@pytest.mark.usefixtures('driver', 'wait')
class TestPlace:
    @pytest.mark.regression
    def test_nine(self, driver, wait, assertion_handling, log_results):
        """
        Functional testing ( deleting comment )
        """
        sa, errors = assertion_handling

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)


@pytest.mark.usefixtures('driver', 'wait')
class TestRegression:
    @pytest.mark.regression
    def test_ten(self, driver, wait, assertion_handling, log_results):
        """
        Regression testing ( checking if all routes work and shown properly )
        """
        sa, errors = assertion_handling

        driver.get(f"{base_url}/")
        sa(driver.current_url == f"{base_url}/", "error occurred while opening home page")

        driver.get(f"{base_url}/game/1")
        sa(driver.current_url == f"{base_url}/game/1", "game page 1 failed to open or does not exist")

        driver.get(f"{base_url}/login")
        sa(driver.current_url == f"{base_url}/login", "error occurred while opening login page")

        admin_login(driver)
        sa(driver.current_url == f"{base_url}/admin", "error occurred while opening admin page")

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)


@pytest.mark.usefixtures('driver', 'wait')
class TestPlace:
    @pytest.mark.regression
    def test_eleven(self, driver, wait, assertion_handling, log_results):
        """
        Smoke testing ( some simple and quick check of general basics of the site altogether :
        navigating through some random game pages, viewing info about the game by switching between GameInfo and Description,
        posting comments and access to admin panel )
        """
        sa, errors = assertion_handling

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)


@pytest.mark.usefixtures('driver', 'wait')
class TestPlace:
    @pytest.mark.regression
    def test_twelve(self, driver, wait, assertion_handling, log_results):
        """
        End-To-End testing ( opening homepage moving to admin panel, logining in, adding whole new game with some test info
        and checking that the game added to the page )
        """
        sa, errors = assertion_handling

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)


@pytest.mark.usefixtures('driver', 'wait')
class TestPlace:
    @pytest.mark.regression
    def test_thirteen(self, driver, wait, assertion_handling, log_results):
        """
        End-To-End testing 2 ( predefined condition : existed comment in database; opening specific game page,
        looking for the comment, then coming to the admin panel, logining in and deleting this comment )
        """
        sa, errors = assertion_handling

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)


@pytest.mark.usefixtures('driver', 'wait')
class TestIntegration:
    @pytest.mark.regression
    def test_fourteen(self, driver, wait, assertion_handling, log_results):
        """
        Integration testing ( adding game to the site and then commenting this game from its game page )
        """
        sa, errors = assertion_handling

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)


@pytest.mark.usefixtures('driver', 'wait')
class TestPlace:
    @pytest.mark.regression
    def test_fifteen(self, driver, wait, assertion_handling, log_results):
        """
        Negative testing for Comment Posting ( trying to post comment without name/text or including
        higher number of symbols into the fields )
        """
        sa, errors = assertion_handling

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)


@pytest.mark.usefixtures('driver', 'wait')
class TestPlace:
    @pytest.mark.regression
    def test_sixteen(self, driver, wait, assertion_handling, log_results):
        """
        Integration testing ( adding new game, then updating info about it, and finally deleting this game from database )
        """
        sa, errors = assertion_handling

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)


# Negative testing ( trying to add game while leaving different fields empty or entering more symbols than the
# maximum allows )
@pytest.mark.usefixtures('driver', 'wait')
class TestPlace:
    @pytest.mark.regression
    def test_seventeen(self, driver, wait, assertion_handling, log_results):
        """Negative testing ( trying to add game while leaving different fields empty or entering more symbols than the
        maximum allows )
        """
        sa, errors = assertion_handling

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)

@pytest.mark.usefixtures('driver', 'wait')
class TestPlace:
    @pytest.mark.regression
    def test_eighteen(self, driver, wait, assertion_handling, log_results):
        """
        Negative testing ( trying to fill other fields then "comment ID" while deleting comment )
        """
        sa, errors = assertion_handling

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)


@pytest.mark.usefixtures('driver', 'wait')
class TestPlace:
    @pytest.mark.regression
    def test_nineteen(self, driver, wait, assertion_handling, log_results):
        """
        Negative testing ( trying to add game with inputted "hyperbolical" data into release date field )
        """
        sa, errors = assertion_handling

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)


@pytest.mark.usefixtures('driver', 'wait')
class TestPlace:
    @pytest.mark.regression
    def test_twenty(self, driver, wait, assertion_handling, log_results):
        """
        Unit testing ( checking that current time prints correctly when adding a comment )
        """
        sa, errors = assertion_handling

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)


@pytest.mark.usefixtures('driver', 'wait')
class TestPlace:
    @pytest.mark.regression
    def test_twentyone(self, driver, wait, assertion_handling, log_results):
        """
        Acceptance testing ( we will imagine that there is a specific requirements provided by the customer telling us that
        the portal should be able to handle some info about few games and will have option to accept comment from any visitor
        of the site by only putting the name, and also there will be an admin panel with ability to add/update/delete
        games and also comment deleting possibility )
        """
        sa, errors = assertion_handling

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)


@pytest.mark.usefixtures('driver', 'wait')
class TestPlace:
    @pytest.mark.regression
    def test_twentytwo(self, driver, wait, assertion_handling, log_results):
        """
        Non-Functional testing ( checking the admin panel page, the buttons, dropdowns etc. )
        """
        sa, errors = assertion_handling

        status = "passed" if not errors else "failed"
        log_results(status, errors)

        if errors:
            formatted_errors = "\n".join([f"{i + 1}. {error}" for i, error in enumerate(errors)])
            pytest.fail(formatted_errors)
