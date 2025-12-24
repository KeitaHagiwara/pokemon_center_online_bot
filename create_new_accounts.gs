// ヘッダー行数を設定
const headerRow = 3
const lastNameMaster = "大谷"
const lastNameKanaMaster = "オオタニ"
const lastNameRomeMaster = "OHTANI"
const dummyNameSheetName = "ダミー名前"

function createNewUser() {

  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const startRow = headerRow + 1; // データ開始行（4行目）

  // ヘッダー辞書を取得
  const headerColumns = createHeaderColumns("accounts", headerRow);

  // 必要な列番号を取得
  const emailCol = headerColumns["メールアドレス"];
  const accountCreatedCol = headerColumns["アカウント作成"];
  const passwordCol = headerColumns["パスワード"];
  const lastNameCol = headerColumns["姓"];
  const firstNameCol = headerColumns["名"];
  const lastNameKanaCol = headerColumns["セイ"];
  const firstNameKanaCol = headerColumns["メイ"];
  const lastNameRomeCol = headerColumns["Sei"];
  const firstNameRomeCol = headerColumns["Mei"];
  const phoneNumberCol = headerColumns["電話番号"];
  const birthdayCol = headerColumns["誕生日"];
  const postalCodeCol = headerColumns["郵便番号"];
  const streetAddressCol = headerColumns["番地"];
  const buildingCol = headerColumns["建物名・部屋番号"];

  // A2, D2, E2, F2の値を取得
  const passwordValue = sheet.getRange("A2").getValue();  // パスワードマスタ
  const birthdayValue = sheet.getRange("D2").getValue();  // 誕生日マスタ
  const postalCodeValue = sheet.getRange("E2").getValue();  // 郵便番号マスタ
  const streetAddressValue = sheet.getRange("F2").getValue(); // 番地マスタ
  const buildingValue = sheet.getRange("G2").getValue();  // 建物名・部屋番号マスタ

  // メールアドレス列の最終行を取得
  const lastRow = sheet.getRange(startRow, emailCol, sheet.getLastRow() - startRow + 1, 1)
    .getValues()
    .reduce((last, row, index) => {
      return row[0] !== "" ? startRow + index : last;
    }, startRow);

  Logger.log("処理対象行: " + startRow + "行目から" + lastRow + "行目まで");

  // データ行をループ処理
  for (let row = startRow; row <= lastRow; row++) {
    // メールアドレスが空白の場合はスキップ
    const email = sheet.getRange(row, emailCol).getValue();
    if (email === "") {
      continue;
    }

    // 「アカウント作成」列の値を取得
    const accountCreated = sheet.getRange(row, accountCreatedCol).getValue();

    // 「ダミー名前」シートのヘッダーカラムを取得
    const headerColumnsDummy = createHeaderColumns(dummyNameSheetName, 1);

    // 「済み」になっていない場合のみ処理
    if (accountCreated !== "済み") {
      // 固有のUIDを生成
      shortUUID = generateCustomShortUUID()

      // ダミーの情報を生成
      dummyRow = getRandomRowFromDummyNames();
      dummyFirstName = dummyRow[headerColumnsDummy["名"] - 1]
      dummyFirstNameKana = dummyRow[headerColumnsDummy["メイ"] - 1]
      dummyFirstNameRome = convertToUpperCase(dummyRow[headerColumnsDummy["Mei"] - 1])
      dummyphoneNumber = generateDummyPhoneNumber()

      // 各列に値を設定
      sheet.getRange(row, passwordCol).setValue(passwordValue);
      sheet.getRange(row, lastNameCol).setValue(lastNameMaster);
      sheet.getRange(row, firstNameCol).setValue(dummyFirstName);
      sheet.getRange(row, lastNameKanaCol).setValue(lastNameKanaMaster);
      sheet.getRange(row, firstNameKanaCol).setValue(dummyFirstNameKana);
      sheet.getRange(row, lastNameRomeCol).setValue(lastNameRomeMaster);
      sheet.getRange(row, firstNameRomeCol).setValue(dummyFirstNameRome);
      sheet.getRange(row, phoneNumberCol).setValue(dummyphoneNumber);
      sheet.getRange(row, birthdayCol).setValue(birthdayValue);
      sheet.getRange(row, postalCodeCol).setValue(postalCodeValue);
      sheet.getRange(row, streetAddressCol).setValue(shortUUID + " " + streetAddressValue)
      sheet.getRange(row, buildingCol).setValue(buildingValue);

      Logger.log(row + "行目を処理しました");
    }
  }

  Logger.log("処理完了");

}


/**
 * 3行目のヘッダーから列名と列番号の辞書を作成する
 * @return {Object} ヘッダー名をキー、列番号を値とする辞書
 */
function createHeaderColumns(sheetName, headerRow=3) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(sheetName);

  // 3行目のデータを取得
  const lastColumn = sheet.getLastColumn();
  const headers = sheet.getRange(headerRow, 1, 1, lastColumn).getValues()[0];

  // 辞書を作成
  const headerColumns = {};
  headers.forEach((header, index) => {
    if (header !== "") { // 空白セルは除外
      headerColumns[header] = index + 1; // 列番号は1始まり
    }
  });

  return headerColumns;
}

/**
 * カスタム長のShortUUIDを生成する
 * @param {number} length - 生成する文字列の長さ
 * @return {string} 指定長のランダム文字列
 */
function generateCustomShortUUID(length = 8) {
  const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
  let result = '';

  for (let i = 0; i < length; i++) {
    const randomIndex = Math.floor(Math.random() * chars.length);
    result += chars[randomIndex];
  }

  return result;
}

/**
 * ダミーの携帯電話番号を生成する（ハイフンなし）
 * 080, 090, 070のいずれかから始まる11桁
 * @return {string} ダミー携帯電話番号（例: 09012345678）
 */
function generateDummyPhoneNumber() {
  const prefixes = ["080", "090", "070"];
  const randomPrefix = prefixes[Math.floor(Math.random() * prefixes.length)];

  // 残り8桁をランダム生成
  let remainingDigits = "";
  for (let i = 0; i < 8; i++) {
    remainingDigits += Math.floor(Math.random() * 10);
  }

  return randomPrefix + remainingDigits;
}

/**
 * 「ダミー名前」シートからランダムで1行を取得する
 * @return {Array} ランダムに選ばれた行のデータ配列
 */
function getRandomRowFromDummyNames() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(dummyNameSheetName);
  headerColDict = createHeaderColumns(dummyNameSheetName, 1)
  Logger.log(headerColDict);

  if (!sheet) {
    throw new Error(`${dummyNameSheetName}という名前のシートが見つかりません`);
  }

  // データ範囲を取得（ヘッダー行を除く）
  const lastRow = sheet.getLastRow();
  const lastColumn = sheet.getLastColumn();

  if (lastRow < 2) {
    throw new Error("データが存在しません（ヘッダー行のみ）");
  }

  // 2行目から最終行までの範囲でランダムな行番号を生成
  const randomRow = Math.floor(Math.random() * (lastRow - 1)) + 2;

  // ランダムな行のデータを取得
  const rowData = sheet.getRange(randomRow, 1, 1, lastColumn).getValues()[0];

  return rowData;
}


/**
 * 半角英数字を全角に変換する
 * @param {string} text - 変換対象のテキスト
 * @return {string} 全角に変換されたテキスト
 */
function convertHalfToFull(text) {
  if (!text) return text;

  return text.replace(/[A-Za-z0-9]/g, function(char) {
    // 半角文字コードから全角文字コードへの変換
    // 半角A-Z: 0x41-0x5A → 全角A-Z: 0xFF21-0xFF3A (差分 0xFEE0)
    // 半角a-z: 0x61-0x7A → 全角a-z: 0xFF41-0xFF5A (差分 0xFEE0)
    // 半角0-9: 0x30-0x39 → 全角0-9: 0xFF10-0xFF19 (差分 0xFEE0)
    return String.fromCharCode(char.charCodeAt(0) + 0xFEE0);
  });
}

/**
 * 小文字のローマ字を大文字に変換する
 * @param {string} text - 変換対象のテキスト
 * @return {string} 大文字に変換されたテキスト
 */
function convertToUpperCase(text) {
  if (!text) return text;
  return text.toUpperCase();
}

