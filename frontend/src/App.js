import React, { useEffect, useState } from 'react';
import { FaCopy } from "react-icons/fa";
import './App.css';
import catalog from './data/catalog.json'
import professors_json from './data/profs.json'
// import tally from './tally.json'

// TODO:
// - make search more robust
// - allow for multiple semesters
// - allow for different types of searches (course, professor, etc.)
// - parse prereqs

const courses = Object.keys(catalog).map(key => catalog[key]);
const professors = Object.keys(professors_json).map(key => professors_json[key]);

let tallyData = [];

function CourseLoader(props) {
  const [elements, setElements] = useState([]);

  useEffect(() => {
    if (tallyData.length > 0) {
      const newElements = props.courses.map(course => {
        let classes = tallyData.filter(cls => (cls.Subj === course.subj) && (cls.Crse === course.crse));
        return <Course key={`${course.subj}${course.crse}`} course={course} classes={classes} />;
      });
      setElements(newElements);
    }
  }, [props.courses]);

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

  let times = props.classItem['Schedule'].split('\n')

  // TODO: make it more robust
  let prof = professors.filter(prof => {
    return prof.tLname.toLowerCase() === props.classItem['Prof'].split(',')[0].toLowerCase();
  })[0];

  return (
    <li className='class-item'>
      <span className='copy-crn' onClick={handleCopy}>{copyText} <FaCopy /> </span>
      <div className='class-item-title'>{props.classItem['Title']}</div>
      <div className='class-item-prof'>
        {prof ? 
        <a href={`https://www.ratemyprofessors.com/professor/${prof.tid}`} target='_blank'>
          Professor: {props.classItem['Prof']}
        </a> : 
        'Professor: ' + props.classItem['Prof']}
        <span className='class-item-prof-rating'>
          {prof && 'rating: (' + prof.overall_rating + ' / 5)'}
          {prof && ' (' + prof.tNumRatings + ' ratings)'}
        </span>
      </div>
      <div className='class-item-times'>
        {times.map((time, idx) => (
          <p key={idx}>{time.trim()}</p>
        ))}
      </div>
      <div className='class-item-enrollment'>
        <div>
          <p>Enrollment: {props.classItem['Enr']} / {props.classItem['Max']}</p>
          <progress value={props.classItem['Enr']} max={props.classItem['Max']}></progress>
        </div>
      </div>
      <div className='class-item-footer-info'><p>CRN: {props.classItem['CRN']} Section: {props.classItem['Sect']}</p></div>
    </li>
  )
}
function Course(props) {
  const [showClasses, setShowClasses] = useState(false);

  const toggleClasses = () => {
    setShowClasses(!showClasses);
  };

  console.log(props.course.preqs);

  return (
    <div className='course-container'>
      <div className='course-title'>{props.course.title}</div>
      <div className='course-creds'>{props.course.creds} credits</div>
      <div className='course-desc'>{props.course.desc}</div>
      <div className='course-preqs'>
        {props.course.preqs && <p>Prerequisites: {props.course.preqs}</p>}
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

function SearchBar(props) {
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
    <div>
      <input
        type="text"
        placeholder="Search..."
        className='search-bar'
        value={searchTerm}
        onChange={(e) => {
          setSearchTerm(e.target.value);
        }}
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            handleSearch(searchTerm);
          }
        }}
      />
      <button className='search-button' onClick={() => handleSearch(searchTerm)}>Search</button>
      <div className='search-results'>
        <CourseLoader courses={searchResults} />
      </div>
    </div>
    );
}

function App() {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      let response = await fetch('http://localhost:8000/tally/202520');
      let data = await response.json();
      tallyData = Object.keys(data).map(key => data[key]);
      setIsLoading(false);
    };
    fetchData();
  }, []);

  return (
    <div className="App">
      <title>Rowan University Course Search</title>
      <header className="App-header">
        <h2>Rowan University Course Search (Spring 2025)</h2>
        <p>Search for courses by title, description, or course code.</p>
        {isLoading ? (<p>Feching data from section tally...</p>) : (<SearchBar/>)}
      </header>
    </div>
  );
}

export default App;
