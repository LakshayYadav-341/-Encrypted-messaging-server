const { PythonShell } = require("python-shell");

const runPythonScript = (scriptName, args = {}) => {
    return new Promise((resolve, reject) => {
        PythonShell.run(scriptName, { args: [JSON.stringify(args)] }, (err, results) => {
            if (err) return reject(err);
            try {
                resolve(JSON.parse(results[0])); // Assume the script outputs JSON
            } catch (parseError) {
                reject(parseError);
            }
        });
    });
};

module.exports = { runPythonScript };
