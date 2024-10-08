import React, { useState } from 'react';
import { FaCopy } from "react-icons/fa";
import './App.css';
import catalog from './catalog.json'
import professors_json from './profs.json'
import tally from './tally.json'

// TODO:
// - make search more robust
// - allow for multiple semesters
// - allow for different types of searches (course, professor, etc.)
// - parse prereqs

const courses = Object.keys(catalog).map(key => catalog[key]);
const professors = Object.keys(professors_json).map(key => professors_json[key]);
const tallyData = Object.keys(tally).map(key => tally[key]);

function CourseLoader(props) {

  let elements = []

  for (const course of props.courses) {
    let classes = tallyData.filter(cls => (cls.Subj === course.subj) && (cls.Crse === course.crse))
    elements.push(<Course course={course} classes={classes}/>)
  }

  return (
    <div>
      {elements}
    </div>
  );
}

function ClassItem(props) {
  const [copyText, setCopyText] = useState('Copy CRN');
  const handleCopy = () => {
    navigator.clipboard.writeText(props.classItem['CRN']);
    setCopyText('Copied!');
    setTimeout(() => setCopyText('Copy CRN'), 2000);
  };

  let times = props.classItem['schedule'].split('\n')

  // TODO: make it more robust
  let prof = professors.filter(prof => {
    return prof.tLname.toLowerCase() === props.classItem['Prof'].split(',')[0].toLowerCase();
  })[0];

  return (
    <li className='class-item' onClick={handleCopy}>
      <span className='copy-crn'>{copyText} <FaCopy /> </span>
      <p>Professor: {props.classItem['Prof']}
        <span className='class-item-prof-rating'>
          {prof && 'rating: (' + prof.overall_rating + ' / 5)'}
          {prof && ' (' + prof.tNumRatings + ' ratings)'}
        </span>
      </p>
      <div className='class-item-times'>
        {times.map((time, idx) => (
          <p key={idx}>{time.trim()}</p>
        ))}
      </div>
      <div className='class-item-enrollment'>
      {props.classItem['Enr'] > 0 && (
        <div>
          <p>Enrollment: {props.classItem['Enr']} / {props.classItem['Max']}</p>
          <progress value={props.classItem['Enr']} max={props.classItem['Max']}></progress>
        </div>
      )}
      </div>
      <div className='class-item-footer-info'><p>CRN: {props.classItem['CRN']} Section: {props.classItem['Sect']}</p></div>
    </li>
  )
}

function LoadPreqs(props){
  const parsePreqs = (preqs) => {
    if (!preqs) return '';
    
    const wordsToRemove = ['Undergraduate level', 'Graduate level', 'Minimum Grade of'];
    
    let parsedPreqs = preqs;
    wordsToRemove.forEach(word => {
      parsedPreqs = parsedPreqs.replace(new RegExp(word, 'g'), '').trim();
    });

    // replace [subj] [crse] with {subj crse}
    parsedPreqs = parsedPreqs.replace(/(\w{2,5}) (\d{5})/g, '{$1 $2}');
    return parsedPreqs;
  };

  let parsedPreqs = parsePreqs(props.preqs);
  
  return parsedPreqs && <p>Prerequisites: {parsedPreqs}</p>
}

function Course(props) {
  const [showClasses, setShowClasses] = useState(false);

  const toggleClasses = () => {
    setShowClasses(!showClasses);
  };

  return (
    <div className='course-container'>
      <div className='course-title'>{props.course.title}</div>
      <div className='course-creds'>{props.course.creds} credits</div>
      <div className='course-desc'>{props.course.desc}</div>
      <div className='course-preqs'>
        <LoadPreqs preqs={props.course.preqs}/>
      </div>
      <button className='show-classes-button' onClick={toggleClasses}>
        {showClasses ? 'Hide Classes' : 'Show Classes'}
      </button>
      {showClasses && (
        <ul className='classes-container'>
          {props.classes.map((classItem, index) => (
            <ClassItem key={index} classItem={classItem} />
          ))}
        </ul>
      )}
    </div>
  );
}

function App() {
  const [searchResults, setSearchResults] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const handleSearch = (searchTerm) => {
    const results = courses.filter(course =>
      course.title.includes(searchTerm) ||
      course.subj.includes(searchTerm) ||
      course.crse.includes(searchTerm));
    setSearchResults(results);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h2>Rowan University Course Search (Spring 2024)</h2>
        <p>Search for courses by title, description, or course code.</p>
        <div className='search-container'>
          <input
            type="text"
            placeholder="Search..."
            className='search-bar'
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleSearch(searchTerm);
              }
            }}
          />
          <button className='search-button' onClick={() => handleSearch(searchTerm)}>Search</button>
        </div>
        <div className='search-results'>
          <CourseLoader courses={searchResults} />
        </div>
      </header>
    </div>
  );
}

export default App;
