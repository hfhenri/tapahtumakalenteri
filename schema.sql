CREATE TABLE Users (
    UserID CHAR(32) PRIMARY KEY,
    Username VARCHAR(50) UNIQUE NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL
);

CREATE TABLE Events (
    EventID CHAR(32) PRIMARY KEY,
    UserID CHAR(32) NOT NULL,
    Title VARCHAR(100) NOT NULL,
    Description TEXT,
    ShortDescription TEXT,
    Price DECIMAL(10, 2) DEFAULT 0.00,
    CategoryID INT,
    ImageID CHAR(32),
    Date TEXT,
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE,
    FOREIGN KEY (ImageID) REFERENCES EventImages(ImageID) ON DELETE CASCADE
);

CREATE TABLE EventImages (
    ImageID CHAR(32) PRIMARY KEY,
    ImageData BLOB,
    FOREIGN KEY (ImageID) REFERENCES Events(ImageID) ON DELETE CASCADE
);

CREATE TABLE Registrations (
    EventID CHAR(32),
    UserID CHAR(32),
    FOREIGN KEY (EventID) REFERENCES Events(EventID) ON DELETE CASCADE,
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE
);

CREATE TABLE Replies (
    QuestionID CHAR(32) UNIQUE PRIMARY KEY,
    ReplyText TEXT
    FOREIGN KEY (QuestionID) REFERENCES Questions(QuestionID) ON DELETE CASCADE,
);

CREATE TABLE Questions (
    QuestionID CHAR(32) UNIQUE,
    EventID CHAR(32) UNIQUE PRIMARY KEY,
    UserID CHAR(32) UNIQUE,
    QuestionText TEXT NOT NULL,
    FOREIGN KEY (EventID) REFERENCES Events(EventID) ON DELETE CASCADE,
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE
);
