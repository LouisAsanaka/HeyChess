let is_promoting = false;
let promote_to = null;
let boardElement = null;
const game = new Chess();
let color = null;

function updateBoard(board) {
    board.position(game.fen(), true);
    is_promoting = false;
}

function makeMove(cfg) {
    // see if the move is legal
    let move = game.move(cfg);
    // illegal move
    if (move === null) return 'snapback';

    socket.emit('play_move', cfg);
}

function setupBoard() {
    const piece_theme = 'static/img/chesspieces/wikipedia/{piece}.png';
    const promotion_dialog = $('#promotion-dialog');

    // do not pick up pieces if the game is over
    // only pick up pieces for the side to move
    const onDragStart = function(source, piece, position, orientation) {
        if (game.game_over() === true
            || color === null
            || (color === game.WHITE) ? (piece.search(/^b/) !== -1) : (piece.search(/^w/) !== -1)
            || color !== game.turn()
        ) {
            return false;
        }
    };

    const onDrop = function(source, target, pieceWithColor, newPos, oldPos, orientation) {
        move_cfg = {
            from: source,
            to: target,
            promotion: 'q'
        };

        // check we are not trying to make an illegal pawn move to the 8th or 1st rank,
        // so the promotion dialog doesn't pop up unnecessarily
        // e.g. (p)d7-f8
        const move = game.move(move_cfg);
        // illegal move
        if (move === null) {
            return 'snapback';
        } else {
            game.undo(); //move is ok, now we can go ahead and check for promotion
        }

        // is it a promotion?
        const source_rank = source.substring(2, 1);
        const target_rank = target.substring(2, 1);

        const piece = game.get(source).type;

        if (piece === 'p' &&
            ((source_rank === '7' && target_rank === '8') || (source_rank === '2' && target_rank === '1'))) {
            is_promoting = true;

            // get piece images
            $('.promotion-piece-q').attr('src', getImgSrc('q'));
            $('.promotion-piece-r').attr('src', getImgSrc('r'));
            $('.promotion-piece-n').attr('src', getImgSrc('n'));
            $('.promotion-piece-b').attr('src', getImgSrc('b'));

            //show the select piece to promote to dialog
            promotion_dialog.dialog({
                modal: true,
                height: 50,
                width: 200,
                resizable: false,
                draggable: false,
                close: onDialogClose,
                closeOnEscape: false,
                dialogClass: 'noTitleStuff'
            }).dialog('widget').position({
                of: $('#board'),
                my: 'middle middle',
                at: 'middle middle',
            });
            //the actual move is made after the piece to promote to
            //has been selected, in the stop event of the promotion piece selectable
            return;
        }
        // no promotion, go ahead and move
        delete move_cfg.promotion;
        makeMove(move_cfg);
    }

    const onSnapEnd = function() {
        if (is_promoting) return; //if promoting we need to select the piece first
        updateBoard(boardElement);
    };

    function getImgSrc(piece) {
        return piece_theme.replace('{piece}', game.turn() + piece.toLocaleUpperCase());
    }

    const onDialogClose = function() {
        move_cfg.promotion = promote_to;
        makeMove(move_cfg);
    }

    // Initialize chessboard
    const cfg = {
        draggable: false,
        onDragStart: onDragStart,
        onDrop: onDrop,
        onSnapEnd: onSnapEnd,
        pieceTheme: piece_theme,
        showNotation: true,
        position: 'start'
    };
    boardElement = ChessBoard('board', cfg);

    // Initialize promotion piece dialog
    $("#promote-to").selectable({
        stop: function() {
            $(".ui-selected", this).each(function() {
                const selectable = $('#promote-to li');
                const index = selectable.index(this);
                if (index > -1) {
                    const promote_to_html = selectable[index].innerHTML;
                    const span = $('<div>' + promote_to_html + '</div>').find('span');
                    promote_to = span[0].innerHTML;
                }
                promotion_dialog.dialog('close');
                $('.ui-selectee').removeClass('ui-selected');
                updateBoard(boardElement);
            });
        }
    });
}

$(document).ready(setupBoard);
$(document).ready(function() {
    socket.on('game_start', function(data) {
        // Close the game over dialog if exists
        if (typeof $('#gameover-dialog').dialog("instance") !== 'undefined') {
            $('#gameover-dialog').dialog("close");
        }
        // Initialize board to starting position
        game.reset();
        boardElement.position('start', false);
        boardElement.draggable(true);
        // Orient the board to the player's color
        color = data[username] == '0' ? game.WHITE : game.BLACK;
        colorLongStr = color === game.WHITE ? 'white' : 'black';
        boardElement.orientation(colorLongStr);
        // Notify!
        window.createNotification({
            positionClass: 'nfc-bottom-right',
            showDuration: 5000,
            theme: 'success'
        })({
            message: "Game started! You are " + colorLongStr + "."
        });
    });

    socket.on('move_played', function(data) {
        if (!(data.hasOwnProperty("from") && data.hasOwnProperty("to"))) {
            return;
        }
        if (data.hasOwnProperty("promotion") && "nbrq".indexOf(data.promotion) === -1) {
            return;
        }
        makeMove(data);
        updateBoard(boardElement);
    });

    socket.on('game_end', function(data) {
        boardElement.draggable(false);
        const dialogElement = $('#gameover-dialog');
        dialogElement.html("");
        dialogElement.append(
            "<span style='display:flex;align-items:center;justify-content:center;height: 100%;font-weight:bold;'>" + data + "</span>"
        );
        dialogElement.dialog({
            draggable: false,
            resizable: false,
            modal: false,
            closeOnEscape: true,
            position: { my: "center", at: "center", of: "#board" },
            title: "Game over!",
            height: 100,
            width: 200,
        });
    });
});