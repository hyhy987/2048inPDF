# Import required modules
import os

PDF_FILE_TEMPLATE = """
%PDF-1.6

% Root
1 0 obj
<<
  /AcroForm <<
    /Fields [ ###FIELD_LIST### ]
  >>
  /Pages 2 0 R
  /OpenAction 17 0 R
  /Type /Catalog
>>
endobj

2 0 obj
<<
  /Count 1
  /Kids [
    16 0 R
  ]
  /Type /Pages
>>

21 0 obj
[
  ###FIELD_LIST###
]
endobj

###FIELDS###

16 0 obj
<<
  /Annots 21 0 R
  /Contents 3 0 R
  /CropBox [
    0.0
    0.0
    612.0
    792.0
  ]
  /MediaBox [
    0.0
    0.0
    612.0
    792.0
  ]
  /Parent 2 0 R
  /Resources <<
    /Font <<
      /F1 22 0 R
    >>
  >>
  /Rotate 0
  /Type /Page
>>
endobj

22 0 obj
<<
  /BaseFont /Helvetica-Bold
  /Encoding /WinAnsiEncoding
  /Name /F1
  /Subtype /Type1
  /Type /Font
>>
endobj

3 0 obj
<< >>
stream
endstream
endobj

17 0 obj
<<
  /JS 42 0 R
  /S /JavaScript
>>
endobj

42 0 obj
<< >>
stream
"""

JAVASCRIPT_CODE = """
var GRID_SIZE = 4;
var grid = [];
var pixel_fields = [];
var score = 0;

// Get color for tile value
function getTileColor(value) {
    switch(value) {
        case 2: return [0.933, 0.894, 0.855];     // #EEE4DA
        case 4: return [0.929, 0.878, 0.784];     // #EDE0C8
        case 8: return [0.949, 0.694, 0.475];     // #F2B179
        case 16: return [0.960, 0.584, 0.388];    // #F59563
        case 32: return [0.965, 0.486, 0.373];    // #F67C5F
        case 64: return [0.965, 0.369, 0.231];    // #F65E3B
        case 128: return [0.929, 0.812, 0.447];   // #EDCF72
        case 256: return [0.929, 0.800, 0.380];   // #EDCC61
        case 512: return [0.929, 0.784, 0.316];   // #EDC850
        case 1024: return [0.929, 0.773, 0.247];  // #EDC53F
        case 2048: return [0.929, 0.761, 0.180];  // #EDC22E
        default: return [0.847, 0.800, 0.749];    // #D8CFC0 for empty cells
    }
}

// Get text color based on tile value
function getTextColor(value) {
    return value <= 4 ? [0.467, 0.431, 0.396] : [0.973, 0.957, 0.945];  // Dark for 2/4, light for others
}

// Initialize the grid with two random tiles
function initializeGrid() {
    // Clear grid and score
    score = 0;

    // Initialize empty grid
    for (var x = 0; x < GRID_SIZE; x++) {
        grid[x] = [];
        pixel_fields[x] = [];
        for (var y = 0; y < GRID_SIZE; y++) {
            grid[x][y] = 0;
            pixel_fields[x][y] = this.getField(`P_${x}_${y}`);
        }
    }

    // Spawn initial tiles
    spawnRandomTile();
    spawnRandomTile();

    // Update display
    drawGrid();
}

// Spawn a random tile with value 2 or 4
function spawnRandomTile() {
    var emptyCells = [];
    for (var x = 0; x < GRID_SIZE; x++) {
        for (var y = 0; y < GRID_SIZE; y++) {
            if (grid[x][y] === 0) {
                emptyCells.push({x: x, y: y});
            }
        }
    }

    if (emptyCells.length > 0) {
        var cell = emptyCells[Math.floor(Math.random() * emptyCells.length)];
        grid[cell.x][cell.y] = Math.random() < 0.9 ? 2 : 4;
        return true;
    }
    return false;
}

// Draw the grid on the PDF
function drawGrid() {
    for (var x = 0; x < GRID_SIZE; x++) {
        for (var y = 0; y < GRID_SIZE; y++) {
            var value = grid[x][y];
            var field = pixel_fields[x][y];

            // Update value
            field.value = value === 0 ? "" : value.toString();

            // Update colors
            var bgColor = getTileColor(value);
            var textColor = getTextColor(value);

            field.fillColor = bgColor;
            field.textColor = textColor;
        }
    }

    // Update score
    this.getField("Score").value = "Score: " + score;
}

// Move tiles in a direction
function moveGrid(direction) {
    var moved = false;
    var merged = Array(GRID_SIZE).fill().map(() => Array(GRID_SIZE).fill(false));

    function processTile(x, y, dx, dy) {
        if (grid[x][y] === 0) return false;

        var newX = x;
        var newY = y;
        var tilesMoved = false;

        // Move tile as far as possible
        while (true) {
            var nextX = newX + dx;
            var nextY = newY + dy;

            if (nextX < 0 || nextX >= GRID_SIZE || nextY < 0 || nextY >= GRID_SIZE) break;
            if (grid[nextX][nextY] !== 0 && grid[nextX][nextY] !== grid[x][y]) break;
            if (grid[nextX][nextY] === grid[x][y] && merged[nextX][nextY]) break;

            newX = nextX;
            newY = nextY;
        }

        if (newX !== x || newY !== y) {
            // Merge if possible
            if (grid[newX][newY] === grid[x][y]) {
                grid[newX][newY] *= 2;
                score += grid[newX][newY];
                merged[newX][newY] = true;
            } else {
                grid[newX][newY] = grid[x][y];
            }
            grid[x][y] = 0;
            tilesMoved = true;
        }

        return tilesMoved;
    }

    // Process all tiles based on direction
    if (direction === "left") {
        for (var y = 0; y < GRID_SIZE; y++)
            for (var x = 0; x < GRID_SIZE; x++)
                if (processTile(x, y, -1, 0)) moved = true;
    }
    else if (direction === "right") {
        for (var y = 0; y < GRID_SIZE; y++)
            for (var x = GRID_SIZE - 1; x >= 0; x--)
                if (processTile(x, y, 1, 0)) moved = true;
    }
    else if (direction === "up") {
        for (var x = 0; x < GRID_SIZE; x++)
            for (var y = 0; y < GRID_SIZE; y++)
                if (processTile(x, y, 0, -1)) moved = true;
    }
    else if (direction === "down") {
        for (var x = 0; x < GRID_SIZE; x++)
            for (var y = GRID_SIZE - 1; y >= 0; y--)
                if (processTile(x, y, 0, 1)) moved = true;
    }

    // Only spawn new tile and update if movement occurred
    if (moved) {
        spawnRandomTile();
        drawGrid();
        if (isGameOver()) {
            app.alert("Game Over! Final Score: " + score);
        }
    }
}

// Check if game is over
function isGameOver() {
    // Check for empty cells
    for (var x = 0; x < GRID_SIZE; x++) {
        for (var y = 0; y < GRID_SIZE; y++) {
            if (grid[x][y] === 0) return false;
        }
    }

    // Check for possible merges
    for (var x = 0; x < GRID_SIZE; x++) {
        for (var y = 0; y < GRID_SIZE; y++) {
            var value = grid[x][y];

            // Check right
            if (x < GRID_SIZE - 1 && grid[x + 1][y] === value) return false;

            // Check down
            if (y < GRID_SIZE - 1 && grid[x][y + 1] === value) return false;
        }
    }

    return true;
}

// Handle WASD keyboard input
function handleKeyInput(event) {
    switch (event.change.toLowerCase()) {
        case 'w': moveGrid("up"); break;
        case 'a': moveGrid("left"); break;
        case 's': moveGrid("down"); break;
        case 'd': moveGrid("right"); break;
    }
}

// Handle button clicks
function handleArrowClick(direction) {
    moveGrid(direction);
}

// Handle keyboard input
function handleKeyPress(event) {
    switch(event.keyCode) {
        case 37: // Left arrow
            moveGrid("left");
            break;
        case 38: // Up arrow
            moveGrid("up");
            break;
        case 39: // Right arrow
            moveGrid("right");
            break;
        case 40: // Down arrow
            moveGrid("down");
            break;
    }
}

//Game button handler
function newGame() {
    initializeGrid();
}

// Initialize game
initializeGrid();

// Add keyboard event listener
this.addKeyDown = true;
this.setKeyDown("handleKeyPress");
"""

PDF_FILE_TEMPLATE_END = """
endstream
endobj

trailer
<<
  /Root 1 0 R
>>

%%EOF
"""

PIXEL_OBJ = """
###IDX### 0 obj
<<
  /FT /Tx
  /Ff 1
  /DA "/F1 24 Tf ###TEXT_COLOR### rg"
  /Q 1
  /MK <<
    /BG ###BG_COLOR###
    /R 8
  >>
  /Border [ 0 0 2 ]
  /P 16 0 R
  /Rect [
    ###RECT###
  ]
  /Subtype /Widget
  /T (P_###X###_###Y###)
  /Type /Annot
>>
endobj
"""

BUTTON_OBJ = """
###IDX### 0 obj
<<
  /A <<
    /JS (###SCRIPT###)
    /S /JavaScript
  >>
  /F 4
  /FT /Btn
  /Ff 65536
  /MK <<
    /BG [
      0.941
      0.929
      0.910
    ]
    /CA (###LABEL###)
    /R 4
  >>
  /P 16 0 R
  /Rect [
    ###RECT###
  ]
  /Subtype /Widget
  /T (###NAME###)
  /Type /Annot
>>
endobj
"""

TEXT_INPUT_OBJ = """
###IDX### 0 obj
<<
  /AA <<
    /K <<
      /JS (handleKeyInput(event))
      /S /JavaScript
    >>
  >>
  /FT /Tx
  /Ff 0
  /DA "/F1 12 Tf 0 0 0 rg"
  /P 16 0 R
  /Rect [
    ###RECT###
  ]
  /Subtype /Widget
  /T (KeyInput)
  /Type /Annot
  /V (Type WASD to move)
>>
endobj
"""

SCORE_OBJ = """
###IDX### 0 obj
<<
  /FT /Tx
  /Ff 1
  /DA "/F1 28 Tf 0.467 0.431 0.396 rg"
  /Q 1
  /MK <<
    /BG [0.973 0.957 0.945]
    /BC [0.467 0.431 0.396]
    /R 8
  >>
  /Border [0 0 2]
  /P 16 0 R
  /Rect [
    ###RECT###
  ]
  /Subtype /Widget
  /T (Score)
  /Type /Annot
  /V (Score: 0)
>>
endobj
"""

BORDER_OBJ = """
###IDX### 0 obj
<<
  /FT /Tx
  /Ff 1
  /DA "/F1 12 Tf 0.467 0.431 0.396 rg"
  /MK <<
    /BG [0.941 0.929 0.910]
    /BC [0.467 0.431 0.396]
    /R 8
  >>
  /Border [0 0 4]
  /P 16 0 R
  /Rect [
    ###RECT###
  ]
  /Subtype /Widget
  /T (Border)
  /Type /Annot
>>
endobj
"""

def generate_pdf():
    PX_SIZE = 80
    GRID_SIZE = 4
    GRID_OFF_X = (612 - (GRID_SIZE * PX_SIZE)) / 2
    GRID_OFF_Y = 600

    # padding between cells
    CELL_PADDING = 4
    # border padding
    BORDER_PADDING = 8

    fields_text = ""
    field_indexes = []
    obj_idx_ctr = 50

    def add_field(field):
        nonlocal fields_text, field_indexes, obj_idx_ctr
        fields_text += field
        field_indexes.append(obj_idx_ctr)
        obj_idx_ctr += 1

    # Add border field first (so it appears behind the grid)
    border = BORDER_OBJ.replace("###IDX###", str(obj_idx_ctr))
    border = border.replace("###RECT###",
        f"{GRID_OFF_X - BORDER_PADDING} "
        f"{GRID_OFF_Y + BORDER_PADDING} "
        f"{GRID_OFF_X + (GRID_SIZE * PX_SIZE) + BORDER_PADDING} "
        f"{GRID_OFF_Y - (GRID_SIZE * PX_SIZE) - BORDER_PADDING}")
    add_field(border)

    # Create a big header "Mum its just a pdf!"
    header_width = 400
    page_width = 612
    header_x_start = (page_width - header_width) / 2
    header_x_end = header_x_start + header_width
    header_field = f"""{obj_idx_ctr} 0 obj
    <<
    /FT /Tx
    /Ff 1
    /DA "/F1 48 Tf 0.965 0.369 0.231 rg"
    /Q 1
    /P 16 0 R
    /MK <<
        /BG [0.973 0.957 0.945]
        /BC [0.965 0.369 0.231]
        /R 8
    >>
    /Border [0 0 3]
    /Rect [
        {header_x_start} {GRID_OFF_Y + 80} {header_x_end} {GRID_OFF_Y + 140}
    ]
    /Subtype /Widget
    /T (Header)
    /Type /Annot
    /V (Mum it's just a pdf!)
    >>
    endobj
    """
    add_field(header_field)
    
    # Create score display
    score_width = GRID_SIZE * PX_SIZE * 0.6
    score_x_start = GRID_OFF_X + (GRID_SIZE * PX_SIZE - score_width) / 2
    score_field = SCORE_OBJ.replace("###IDX###", str(obj_idx_ctr))
    score_field = score_field.replace("###RECT###",
        f"{score_x_start} {GRID_OFF_Y + 20} {score_x_start + score_width} {GRID_OFF_Y + 50}")
    add_field(score_field)

    # Add WASD text input field
    input_field = TEXT_INPUT_OBJ.replace("###IDX###", str(obj_idx_ctr))
    input_field = input_field.replace("###RECT###",
        f"{GRID_OFF_X} {GRID_OFF_Y - (GRID_SIZE * PX_SIZE) - 240} {GRID_OFF_X + GRID_SIZE * PX_SIZE} {GRID_OFF_Y - (GRID_SIZE * PX_SIZE) - 220}")
    add_field(input_field)

    # Create grid with padding
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            pixel = PIXEL_OBJ
            pixel = pixel.replace("###IDX###", str(obj_idx_ctr))
            pixel = pixel.replace("###RECT###",
                f"{GRID_OFF_X + x * PX_SIZE + CELL_PADDING} "
                f"{GRID_OFF_Y - y * PX_SIZE - CELL_PADDING} "
                f"{GRID_OFF_X + (x + 1) * PX_SIZE - CELL_PADDING} "
                f"{GRID_OFF_Y - (y + 1) * PX_SIZE + CELL_PADDING}")
            pixel = pixel.replace("###X###", str(x))
            pixel = pixel.replace("###Y###", str(y))
            pixel = pixel.replace("###BG_COLOR###", "[0.847 0.800 0.749]")
            pixel = pixel.replace("###TEXT_COLOR###", "0.467 0.431 0.396")
            add_field(pixel)

    # Add control buttons
    button_size = 50
    arrow_buttons = [
        ("UP", "Up", GRID_OFF_X + PX_SIZE * 1.69, GRID_OFF_Y - (GRID_SIZE * PX_SIZE) - 80, "handleArrowClick('up')"),
        ("LEFT", "Left", GRID_OFF_X + PX_SIZE * 0.69, GRID_OFF_Y - (GRID_SIZE * PX_SIZE) - 120, "handleArrowClick('left')"),
        ("DOWN", "Down", GRID_OFF_X + PX_SIZE * 1.69, GRID_OFF_Y - (GRID_SIZE * PX_SIZE) - 160, "handleArrowClick('down')"),
        ("RIGHT", "Right", GRID_OFF_X + PX_SIZE * 2.69, GRID_OFF_Y - (GRID_SIZE * PX_SIZE) - 120, "handleArrowClick('right')")
    ]

    for label, name, x, y, script in arrow_buttons:
        button = BUTTON_OBJ.replace("###IDX###", str(obj_idx_ctr))
        button = button.replace("###LABEL###", label)
        button = button.replace("###NAME###", name)
        button = button.replace("###SCRIPT###", script)
        button = button.replace("###RECT###", f"{x} {y} {x + button_size} {y + button_size}")
        add_field(button)

    # Add New Game button
    new_game_button = BUTTON_OBJ.replace("###IDX###", str(obj_idx_ctr))
    new_game_button = new_game_button.replace("###LABEL###", "New Game")
    new_game_button = new_game_button.replace("###NAME###", "NewGame")
    new_game_button = new_game_button.replace("###SCRIPT###", "newGame()")
    new_game_button = new_game_button.replace("###RECT###",
        f"{GRID_OFF_X} {GRID_OFF_Y - (GRID_SIZE * PX_SIZE) - 220} {GRID_OFF_X + GRID_SIZE * PX_SIZE} {GRID_OFF_Y - (GRID_SIZE * PX_SIZE) - 180}")

    add_field(new_game_button)

    # Generate PDF content
    pdf_content = (
        PDF_FILE_TEMPLATE.replace("###FIELDS###", fields_text)
        .replace("###FIELD_LIST###", " ".join([f"{i} 0 R" for i in field_indexes]))
        + JAVASCRIPT_CODE
        + PDF_FILE_TEMPLATE_END
    )

    # Save to file
    with open("2048_game.pdf", "wb") as pdf_file:
        pdf_file.write(pdf_content.encode('utf-8'))

if __name__ == "__main__":
    try:
        generate_pdf()
        print("PDF generated successfully! Open '2048_game.pdf' to play the game.")
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")