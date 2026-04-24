USE musicdb;

CREATE TABLE IF NOT EXISTS artist_user (
    UserID INT NOT NULL,
    ArtistID INT NOT NULL,
    RoleLabel VARCHAR(20) NOT NULL DEFAULT 'artist',
    CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (UserID, ArtistID),
    UNIQUE KEY ux_artist_user_user (UserID),
    UNIQUE KEY ux_artist_user_artist (ArtistID),
    CONSTRAINT fk_artist_user_user FOREIGN KEY (UserID) REFERENCES users (UserID),
    CONSTRAINT fk_artist_user_artist FOREIGN KEY (ArtistID) REFERENCES artist (ArtistID)
);

CREATE TABLE IF NOT EXISTS user_follow (
    FollowerUserID INT NOT NULL,
    FollowedUserID INT NOT NULL,
    CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (FollowerUserID, FollowedUserID),
    CONSTRAINT fk_user_follow_follower FOREIGN KEY (FollowerUserID) REFERENCES users (UserID),
    CONSTRAINT fk_user_follow_followed FOREIGN KEY (FollowedUserID) REFERENCES users (UserID)
);

CREATE TABLE IF NOT EXISTS artist_follow (
    UserID INT NOT NULL,
    ArtistID INT NOT NULL,
    CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (UserID, ArtistID),
    CONSTRAINT fk_artist_follow_user FOREIGN KEY (UserID) REFERENCES users (UserID),
    CONSTRAINT fk_artist_follow_artist FOREIGN KEY (ArtistID) REFERENCES artist (ArtistID)
);

DELIMITER $$

DROP FUNCTION IF EXISTS GetUserFollowerCount$$
CREATE FUNCTION GetUserFollowerCount(p_user_id INT)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE v_count INT;
    SELECT COUNT(*) INTO v_count
    FROM user_follow
    WHERE FollowedUserID = p_user_id;
    RETURN v_count;
END$$

DROP FUNCTION IF EXISTS GetUserFollowingCount$$
CREATE FUNCTION GetUserFollowingCount(p_user_id INT)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE v_count INT;
    SELECT COUNT(*) INTO v_count
    FROM user_follow
    WHERE FollowerUserID = p_user_id;
    RETURN v_count;
END$$

DROP FUNCTION IF EXISTS GetArtistFollowerCount$$
CREATE FUNCTION GetArtistFollowerCount(p_artist_id INT)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE v_count INT;
    SELECT COUNT(*) INTO v_count
    FROM artist_follow
    WHERE ArtistID = p_artist_id;
    RETURN v_count;
END$$

DROP FUNCTION IF EXISTS GetTrackTotalStreams$$
CREATE FUNCTION GetTrackTotalStreams(p_track_id INT)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE v_count INT;
    SELECT COALESCE(SUM(StreamCount), 0) INTO v_count
    FROM royalty
    WHERE Track_TrackID = p_track_id;
    RETURN COALESCE(v_count, 0);
END$$

DROP FUNCTION IF EXISTS GetAlbumDuration$$
CREATE FUNCTION GetAlbumDuration(p_album_id INT)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE v_duration INT;
    SELECT COALESCE(SUM(t.Duration), 0) INTO v_duration
    FROM track t
    WHERE t.Album_AlbumID = p_album_id;
    RETURN v_duration;
END$$

DROP FUNCTION IF EXISTS GetAlbumTrackCount$$
CREATE FUNCTION GetAlbumTrackCount(p_album_id INT)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE v_count INT;
    SELECT COUNT(*) INTO v_count
    FROM track t
    WHERE t.Album_AlbumID = p_album_id;
    RETURN v_count;
END$$

DROP PROCEDURE IF EXISTS RecordStreamEvent$$
CREATE PROCEDURE RecordStreamEvent(
    IN p_user_id INT,
    IN p_track_id INT,
    IN p_device_type VARCHAR(50),
    IN p_country VARCHAR(50)
)
BEGIN
    INSERT INTO streamlog (
        StartTime, EndTime, StreamDuration, WasCompleted, SkippedAt,
        DeviceType, Country, Users_UserID, Track_TrackID
    )
    VALUES (NOW(), NULL, NULL, NULL, NULL, p_device_type, p_country, p_user_id, p_track_id);
END$$

DROP PROCEDURE IF EXISTS RecordStreamWithRoyaltyUpdate$$
CREATE PROCEDURE RecordStreamWithRoyaltyUpdate(
    IN p_user_id INT,
    IN p_track_id INT,
    IN p_device_type VARCHAR(50),
    IN p_country VARCHAR(50)
)
BEGIN
    INSERT INTO streamlog (
        StartTime, EndTime, StreamDuration, WasCompleted, SkippedAt,
        DeviceType, Country, Users_UserID, Track_TrackID
    )
    VALUES (NOW(), NULL, NULL, NULL, NULL, p_device_type, p_country, p_user_id, p_track_id);

    UPDATE royalty
    SET StreamCount = COALESCE(StreamCount, 0) + 1
    WHERE Track_TrackID = p_track_id;
END$$

DROP PROCEDURE IF EXISTS EndStreamEvent$$
CREATE PROCEDURE EndStreamEvent(
    IN p_stream_id INT,
    IN p_user_id INT,
    IN p_was_completed INT,
    IN p_skipped_at INT
)
BEGIN
    UPDATE streamlog
    SET EndTime = NOW(),
        StreamDuration = TIMESTAMPDIFF(SECOND, StartTime, NOW()),
        WasCompleted = p_was_completed,
        SkippedAt = p_skipped_at
    WHERE StreamID = p_stream_id AND Users_UserID = p_user_id;
END$$

DROP PROCEDURE IF EXISTS BookTicketWithValidation$$
CREATE PROCEDURE BookTicketWithValidation(
    IN p_user_id INT,
    IN p_show_id INT,
    IN p_price DECIMAL(10,2),
    IN p_seat_section VARCHAR(20),
    IN p_seat_row VARCHAR(20),
    IN p_seat_number VARCHAR(20),
    IN p_seat_category VARCHAR(50),
    OUT p_result VARCHAR(100)
)
BEGIN
    DECLARE v_exists INT DEFAULT 0;

    SELECT COUNT(*) INTO v_exists
    FROM ticket
    WHERE Show_ShowID = p_show_id
      AND SeatSection = p_seat_section
      AND SeatRow = p_seat_row
      AND SeatNumber = p_seat_number
      AND COALESCE(Status, 'Booked') <> 'Cancelled';

    IF v_exists > 0 THEN
        SET p_result = 'SEAT_ALREADY_BOOKED';
    ELSE
        INSERT INTO ticket (
            Price, PurchaseDate, Status, SeatSection, SeatRow, SeatNumber,
            SeatCategory, Show_ShowID, Users_UserID
        )
        VALUES (
            p_price, NOW(), 'Booked', p_seat_section, p_seat_row, p_seat_number,
            p_seat_category, p_show_id, p_user_id
        );
        SET p_result = 'BOOKED';
    END IF;
END$$

DROP PROCEDURE IF EXISTS CancelTicketBooking$$
CREATE PROCEDURE CancelTicketBooking(
    IN p_ticket_id INT,
    IN p_user_id INT,
    OUT p_result INT
)
BEGIN
    UPDATE ticket
    SET Status = 'Cancelled'
    WHERE TicketID = p_ticket_id AND Users_UserID = p_user_id;

    SET p_result = ROW_COUNT();
END$$

DROP PROCEDURE IF EXISTS RefreshRoyaltyStreamCounts$$
CREATE PROCEDURE RefreshRoyaltyStreamCounts()
BEGIN
    UPDATE royalty r
    SET r.StreamCount = (
        SELECT COALESCE(COUNT(sl.StreamID), 0)
        FROM streamlog sl
        WHERE sl.Track_TrackID = r.Track_TrackID
    );
END$$

DROP TRIGGER IF EXISTS after_stream_insert$$
CREATE TRIGGER after_stream_insert
AFTER INSERT ON streamlog
FOR EACH ROW
BEGIN
    UPDATE royalty
    SET StreamCount = COALESCE(StreamCount, 0) + 1
    WHERE Track_TrackID = NEW.Track_TrackID;
END$$

DROP TRIGGER IF EXISTS prevent_duplicate_seat_booking$$
CREATE TRIGGER prevent_duplicate_seat_booking
BEFORE INSERT ON ticket
FOR EACH ROW
BEGIN
    IF EXISTS (
        SELECT 1
        FROM ticket
        WHERE Show_ShowID = NEW.Show_ShowID
          AND SeatSection = NEW.SeatSection
          AND SeatRow = NEW.SeatRow
          AND SeatNumber = NEW.SeatNumber
          AND COALESCE(Status, 'Booked') <> 'Cancelled'
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Seat already booked for this show';
    END IF;
END$$

DROP TRIGGER IF EXISTS before_user_follow_insert$$
CREATE TRIGGER before_user_follow_insert
BEFORE INSERT ON user_follow
FOR EACH ROW
BEGIN
    IF NEW.FollowerUserID = NEW.FollowedUserID THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A user cannot follow themselves';
    END IF;
END$$

DROP TRIGGER IF EXISTS before_artist_follow_insert$$
CREATE TRIGGER before_artist_follow_insert
BEFORE INSERT ON artist_follow
FOR EACH ROW
BEGIN
    IF EXISTS (
        SELECT 1
        FROM artist_follow
        WHERE UserID = NEW.UserID AND ArtistID = NEW.ArtistID
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'User already follows this artist';
    END IF;
END$$

DELIMITER ;

INSERT IGNORE INTO artist_user (UserID, ArtistID, RoleLabel)
VALUES
    (1, 1, 'artist'),
    (2, 2, 'artist'),
    (3, 3, 'artist'),
    (4, 4, 'artist'),
    (5, 5, 'artist');

INSERT IGNORE INTO user_follow (FollowerUserID, FollowedUserID)
VALUES
    (1, 2),
    (1, 3),
    (2, 1),
    (3, 1),
    (4, 2),
    (5, 1);

INSERT IGNORE INTO artist_follow (UserID, ArtistID)
VALUES
    (1, 2),
    (1, 5),
    (2, 1),
    (2, 3),
    (3, 2),
    (4, 1),
    (5, 5);
